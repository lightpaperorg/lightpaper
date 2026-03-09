"""Writing IDE API: sessions, files, messages, and chat streaming."""

import hashlib
import hmac
import logging
import secrets
import time

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import Account, ApiKey, WritingFile, WritingMessage, WritingSession
from app.rate_limit import limiter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/write", tags=["write"])


# --- Session cookie auth ---


def _sign_token(account_id: str) -> str:
    """Create a signed session token: account_id.timestamp.signature."""
    ts = str(int(time.time()))
    payload = f"{account_id}.{ts}"
    sig = hmac.new(
        settings.ide_session_secret.encode(), payload.encode(), hashlib.sha256
    ).hexdigest()[:32]
    return f"{payload}.{sig}"


def _verify_token(token: str) -> str | None:
    """Verify a session token, return account_id or None."""
    parts = token.split(".")
    if len(parts) != 3:
        return None
    account_id, ts, sig = parts
    payload = f"{account_id}.{ts}"
    expected = hmac.new(
        settings.ide_session_secret.encode(), payload.encode(), hashlib.sha256
    ).hexdigest()[:32]
    if not hmac.compare_digest(sig, expected):
        return None
    # Expire after 30 days
    if time.time() - int(ts) > 30 * 86400:
        return None
    return account_id


async def require_ide_session(
    request: Request,
    lp_session: str | None = Cookie(None),
    db: AsyncSession = Depends(get_db),
) -> Account:
    """Authenticate via IDE session cookie."""
    if not lp_session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    account_id = _verify_token(lp_session)
    if not account_id:
        raise HTTPException(status_code=401, detail="Session expired")
    result = await db.execute(
        select(Account).where(Account.id == account_id, Account.deleted_at.is_(None))
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=401, detail="Account not found")
    return account


# --- Schemas ---


class CreateSessionRequest(BaseModel):
    title: str
    book_config: dict = {}


class UpdateFileRequest(BaseModel):
    content: str


class ChatRequest(BaseModel):
    message: str


class LoginRequest(BaseModel):
    api_key: str


class EmailLoginRequest(BaseModel):
    email: str


class EmailVerifyRequest(BaseModel):
    session_id: str
    code: str


# --- Auth endpoints ---


def _set_session_cookie(response: Response, account_id: str):
    """Set the IDE session cookie."""
    session_token = _sign_token(account_id)
    response.set_cookie(
        key="lp_session",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=30 * 86400,
        path="/",
    )


@router.post("/auth/login")
async def ide_login(body: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    """Exchange an API key for an IDE session cookie."""
    import bcrypt

    token = body.api_key
    prefix = token[:8]
    result = await db.execute(
        select(ApiKey).where(ApiKey.key_prefix == prefix, ApiKey.revoked_at.is_(None))
    )
    keys = result.scalars().all()

    for key in keys:
        if bcrypt.checkpw(token.encode("utf-8"), key.key_hash.encode("utf-8")):
            acct_result = await db.execute(
                select(Account).where(Account.id == key.account_id, Account.deleted_at.is_(None))
            )
            account = acct_result.scalar_one_or_none()
            if account:
                _set_session_cookie(response, str(account.id))
                return {
                    "handle": account.handle,
                    "display_name": account.display_name,
                    "gravity_level": account.gravity_level,
                }

    raise HTTPException(status_code=401, detail="Invalid API key")


@router.post("/auth/email")
@limiter.limit("5/hour")
async def ide_email_login(
    request: Request,
    body: EmailLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Send a 6-digit OTP code to the given email for IDE login."""
    import hashlib as hl
    from datetime import UTC, datetime, timedelta

    from sqlalchemy import func

    from app.models import EmailAuthSession
    from app.services.email import send_otp_email

    email = body.email.strip().lower()

    # Per-email rate limit: max 3 codes/hour
    one_hour_ago = datetime.now(UTC) - timedelta(hours=1)
    count_result = await db.execute(
        select(func.count())
        .select_from(EmailAuthSession)
        .where(
            func.lower(EmailAuthSession.email) == email,
            EmailAuthSession.created_at >= one_hour_ago,
        )
    )
    recent_count = count_result.scalar() or 0
    if recent_count >= 3:
        raise HTTPException(status_code=429, detail="Too many codes sent. Try again in an hour.")

    # Generate code + session
    code = str(secrets.randbelow(900000) + 100000)
    code_hash = hl.sha256(code.encode()).hexdigest()
    session_id = secrets.token_urlsafe(24)

    email_session = EmailAuthSession(
        session_id=session_id,
        email=email,
        code_hash=code_hash,
        expires_at=datetime.now(UTC) + timedelta(minutes=10),
    )
    db.add(email_session)
    await db.commit()

    sent = await send_otp_email(email, code)
    if not sent:
        logger.warning("OTP email delivery failed for IDE session %s", session_id)

    # Mask email for display
    local, domain = email.split("@", 1)
    masked = f"{local[0]}***@{domain}"
    return {"session_id": session_id, "message": f"Code sent to {masked}"}


@router.post("/auth/verify")
@limiter.limit("10/hour")
async def ide_email_verify(
    request: Request,
    body: EmailVerifyRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Verify OTP code and set IDE session cookie. Creates account if new."""
    import hashlib as hl
    from datetime import UTC, datetime

    from sqlalchemy import func
    from sqlalchemy.exc import IntegrityError

    from app.models import EmailAuthSession

    result = await db.execute(
        select(EmailAuthSession).where(EmailAuthSession.session_id == body.session_id)
    )
    email_session = result.scalar_one_or_none()
    if not email_session:
        raise HTTPException(status_code=404, detail="Session not found.")
    if email_session.verified_at:
        raise HTTPException(status_code=410, detail="Session already used.")
    if datetime.now(UTC) > email_session.expires_at:
        raise HTTPException(status_code=410, detail="Code expired. Request a new one.")
    if email_session.attempts >= email_session.max_attempts:
        raise HTTPException(status_code=429, detail="Too many attempts. Request a new code.")

    # Check code
    email_session.attempts += 1
    code_hash = hl.sha256(body.code.encode()).hexdigest()
    if not hmac.compare_digest(code_hash, email_session.code_hash):
        await db.commit()
        remaining = email_session.max_attempts - email_session.attempts
        raise HTTPException(status_code=401, detail=f"Wrong code. {remaining} attempt(s) remaining.")

    # Code correct
    email_session.verified_at = datetime.now(UTC)

    # Find or create account
    email = email_session.email.lower()
    acct_result = await db.execute(
        select(Account).where(
            func.lower(Account.email) == email,
            Account.deleted_at.is_(None),
        )
    )
    account = acct_result.scalar_one_or_none()

    if not account:
        account = Account(
            firebase_uid=None,
            display_name=email.split("@")[0],
            email=email_session.email,
        )
        db.add(account)
        try:
            await db.flush()
        except IntegrityError:
            await db.rollback()
            email_session.verified_at = datetime.now(UTC)
            db.add(email_session)
            acct_result = await db.execute(
                select(Account).where(
                    func.lower(Account.email) == email,
                    Account.deleted_at.is_(None),
                )
            )
            account = acct_result.scalar_one_or_none()
            if not account:
                raise HTTPException(status_code=500, detail="Account creation failed.")

    await db.commit()
    await db.refresh(account)

    # Set session cookie
    _set_session_cookie(response, str(account.id))

    return {
        "handle": account.handle,
        "display_name": account.display_name or email.split("@")[0],
        "email": account.email,
        "gravity_level": account.gravity_level,
    }


@router.post("/auth/logout")
async def ide_logout(response: Response):
    """Clear the IDE session cookie."""
    response.delete_cookie("lp_session", path="/")
    return {"ok": True}


@router.get("/auth/me")
async def ide_me(account: Account = Depends(require_ide_session)):
    """Get current authenticated user."""
    return {
        "id": str(account.id),
        "handle": account.handle,
        "display_name": account.display_name,
        "email": account.email,
        "gravity_level": account.gravity_level,
    }


# --- Session CRUD ---


def _generate_session_id() -> str:
    return "ws_" + secrets.token_urlsafe(8)


@router.post("/sessions")
async def create_session(
    body: CreateSessionRequest,
    account: Account = Depends(require_ide_session),
    db: AsyncSession = Depends(get_db),
):
    """Create a new writing session."""
    # Check session limit
    from app.routes.billing import SESSION_LIMITS

    tier = account.tier or "free"
    limit = SESSION_LIMITS.get(tier, SESSION_LIMITS["free"])
    result_count = await db.execute(
        select(WritingSession).where(
            WritingSession.account_id == account.id,
            WritingSession.deleted_at.is_(None),
        )
    )
    if len(result_count.scalars().all()) >= limit:
        raise HTTPException(
            status_code=403,
            detail=f"{tier} tier limited to {limit} session(s). Delete a session or upgrade to Pro.",
        )

    session = WritingSession(
        id=_generate_session_id(),
        account_id=account.id,
        title=body.title,
        book_config=body.book_config,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return {
        "id": session.id,
        "title": session.title,
        "status": session.status,
        "current_wave": session.current_wave,
        "created_at": session.created_at.isoformat(),
    }


@router.get("/sessions")
async def list_sessions(
    account: Account = Depends(require_ide_session),
    db: AsyncSession = Depends(get_db),
):
    """List all writing sessions for the authenticated user."""
    result = await db.execute(
        select(WritingSession)
        .where(
            WritingSession.account_id == account.id,
            WritingSession.deleted_at.is_(None),
        )
        .order_by(WritingSession.updated_at.desc())
    )
    sessions = result.scalars().all()
    return [
        {
            "id": s.id,
            "title": s.title,
            "status": s.status,
            "current_wave": s.current_wave,
            "total_tokens_used": s.total_tokens_used,
            "published_book_id": s.published_book_id,
            "created_at": s.created_at.isoformat(),
            "updated_at": s.updated_at.isoformat(),
        }
        for s in sessions
    ]


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    account: Account = Depends(require_ide_session),
    db: AsyncSession = Depends(get_db),
):
    """Get a writing session with its file tree."""
    session = await _load_session(session_id, account, db)
    files = await _load_files(session_id, db)
    return {
        "id": session.id,
        "title": session.title,
        "status": session.status,
        "current_wave": session.current_wave,
        "wave_state": session.wave_state,
        "book_config": session.book_config,
        "total_tokens_used": session.total_tokens_used,
        "published_book_id": session.published_book_id,
        "created_at": session.created_at.isoformat(),
        "updated_at": session.updated_at.isoformat(),
        "files": files,
    }


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    account: Account = Depends(require_ide_session),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete a writing session."""
    session = await _load_session(session_id, account, db)
    from sqlalchemy import text as sql_text
    await db.execute(
        update(WritingSession)
        .where(WritingSession.id == session.id)
        .values(deleted_at=sql_text("NOW()"))
    )
    await db.commit()
    return Response(status_code=204)


# --- Files ---


@router.get("/sessions/{session_id}/files")
async def list_files(
    session_id: str,
    account: Account = Depends(require_ide_session),
    db: AsyncSession = Depends(get_db),
):
    """Get all files for a session, grouped by wave."""
    await _load_session(session_id, account, db)
    return await _load_files(session_id, db)


@router.get("/sessions/{session_id}/files/{file_id}")
async def get_file(
    session_id: str,
    file_id: str,
    account: Account = Depends(require_ide_session),
    db: AsyncSession = Depends(get_db),
):
    """Get a single file's content."""
    await _load_session(session_id, account, db)
    result = await db.execute(
        select(WritingFile).where(WritingFile.id == file_id, WritingFile.session_id == session_id)
    )
    f = result.scalar_one_or_none()
    if not f:
        raise HTTPException(status_code=404, detail="File not found")
    return {
        "id": str(f.id),
        "wave": f.wave,
        "file_type": f.file_type,
        "chapter_number": f.chapter_number,
        "title": f.title,
        "content": f.content,
        "word_count": f.word_count,
    }


@router.put("/sessions/{session_id}/files/{file_id}")
async def update_file(
    session_id: str,
    file_id: str,
    body: UpdateFileRequest,
    account: Account = Depends(require_ide_session),
    db: AsyncSession = Depends(get_db),
):
    """Update a file's content (author edits)."""
    await _load_session(session_id, account, db)
    result = await db.execute(
        select(WritingFile).where(WritingFile.id == file_id, WritingFile.session_id == session_id)
    )
    f = result.scalar_one_or_none()
    if not f:
        raise HTTPException(status_code=404, detail="File not found")
    word_count = len(body.content.split())
    await db.execute(
        update(WritingFile)
        .where(WritingFile.id == f.id)
        .values(content=body.content, word_count=word_count)
    )
    await db.commit()
    return {"ok": True, "word_count": word_count}


# --- Messages ---


@router.get("/sessions/{session_id}/messages")
async def list_messages(
    session_id: str,
    wave: int | None = None,
    account: Account = Depends(require_ide_session),
    db: AsyncSession = Depends(get_db),
):
    """Get chat messages for a session, optionally filtered by wave."""
    await _load_session(session_id, account, db)
    query = (
        select(WritingMessage)
        .where(WritingMessage.session_id == session_id)
        .order_by(WritingMessage.created_at)
    )
    if wave is not None:
        query = query.where(WritingMessage.wave == wave)
    result = await db.execute(query)
    msgs = result.scalars().all()
    return [
        {
            "id": str(m.id),
            "wave": m.wave,
            "role": m.role,
            "content": m.content,
            "files_generated": m.files_generated,
            "created_at": m.created_at.isoformat(),
        }
        for m in msgs
    ]


# --- Chat (streaming with tool_use for file creation) ---

# Tool definitions for Claude
SAVE_FILE_TOOL = {
    "name": "save_file",
    "description": "Save content as a file in the author's manuscript. Use this whenever you produce substantial content that the author should be able to review, edit, and navigate — outlines, chapter openings, pivotal scenes, full chapter drafts, research notes, etc.",
    "input_schema": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "Short title for the file (e.g., 'Chapter 3: Scene Outline', 'Wave 2 Opening: The Arrival')",
            },
            "content": {
                "type": "string",
                "description": "The full markdown content of the file",
            },
            "file_type": {
                "type": "string",
                "enum": ["research", "outline", "opening", "pivotal_scene", "draft", "edited", "notes"],
                "description": "Type of content",
            },
            "chapter_number": {
                "type": "integer",
                "description": "Chapter number if this is chapter-specific content (omit for non-chapter files)",
            },
        },
        "required": ["title", "content", "file_type"],
    },
}

RESEARCH_TOOL = {
    "name": "research",
    "description": "Spawn a focused research sub-agent to investigate a topic in depth. Use this when you need to think deeply about historical context, technical details, character psychology, plot mechanics, narrative structure, or any subject that would benefit from dedicated analysis before incorporating into the manuscript. The sub-agent will return a detailed research brief.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The research question or topic to investigate in depth",
            },
            "context": {
                "type": "string",
                "description": "Relevant context from the manuscript — what you already know and what specifically you need to learn",
            },
        },
        "required": ["query"],
    },
}

WEB_SEARCH_TOOL = {
    "name": "web_search",
    "description": "Search the web for information. Use this to find facts, historical details, technical specifics, cultural context, real-world references, or anything that would make the writing more authentic and grounded. Returns search results with titles, URLs, and descriptions.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query",
            },
            "count": {
                "type": "integer",
                "description": "Number of results to return (default 5, max 10)",
            },
        },
        "required": ["query"],
    },
}

WEB_FETCH_TOOL = {
    "name": "web_fetch",
    "description": "Fetch and read a web page. Use this after web_search to read the full content of a promising result, or to read any URL the author shares. Returns the page text content (HTML stripped).",
    "input_schema": {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The URL to fetch",
            },
        },
        "required": ["url"],
    },
}


@router.post("/sessions/{session_id}/chat")
@limiter.limit("30/minute")
async def chat(
    request: Request,
    session_id: str,
    body: ChatRequest,
    account: Account = Depends(require_ide_session),
    db: AsyncSession = Depends(get_db),
):
    """Send a message and get a streaming response from Claude with file creation via tool_use."""
    session = await _load_session(session_id, account, db)

    if not settings.anthropic_api_key:
        raise HTTPException(status_code=503, detail="AI service not configured")

    # Check token limit
    from app.routes.billing import TOKEN_LIMITS

    tier = account.tier or "free"
    token_limit = TOKEN_LIMITS.get(tier, TOKEN_LIMITS["free"])
    if session.total_tokens_used >= token_limit:
        raise HTTPException(
            status_code=403,
            detail=f"Token limit reached ({token_limit:,} tokens). Upgrade to Pro for more.",
        )

    # Save user message
    user_msg = WritingMessage(
        session_id=session.id,
        wave=session.current_wave,
        role="user",
        content=body.message,
    )
    db.add(user_msg)
    await db.commit()

    # Build conversation context
    from app.services.wave_engine import build_messages, get_system_prompt

    system_prompt = get_system_prompt(session)
    messages = await build_messages(session, db)

    # We need the session ID and wave in the stream closure
    session_id_val = session.id
    current_wave = session.current_wave

    async def stream():
        import json

        import anthropic

        client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        full_text_response = ""
        total_tokens = 0
        created_file_ids = []

        try:
            # Use non-streaming for tool_use support, but stream text chunks
            # We'll loop to handle tool_use responses
            conv_messages = list(messages)
            max_turns = 10  # Allow search → fetch → research → write chains

            for _ in range(max_turns):
                response = await client.messages.create(
                    model="claude-opus-4-6",
                    max_tokens=16000,
                    thinking={
                        "type": "enabled",
                        "budget_tokens": 10000,
                    },
                    system=system_prompt,
                    messages=conv_messages,
                    tools=[SAVE_FILE_TOOL, RESEARCH_TOOL, WEB_SEARCH_TOOL, WEB_FETCH_TOOL],
                )

                total_tokens += response.usage.input_tokens + response.usage.output_tokens

                # Process content blocks
                tool_results = []
                for block in response.content:
                    if block.type == "thinking":
                        # Extended thinking — don't send to frontend
                        continue
                    elif block.type == "text":
                        full_text_response += block.text
                        yield f"data: {json.dumps({'type': 'text', 'content': block.text})}\n\n"
                    elif block.type == "tool_use" and block.name == "research":
                        # Spawn a research sub-agent
                        try:
                            yield f"data: {json.dumps({'type': 'text', 'content': '\\n\\n*Researching...*\\n\\n'})}\n\n"
                            research_result = await _run_research(
                                client, block.input.get("query", ""),
                                block.input.get("context", ""),
                                session_id_val,
                            )
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": research_result,
                            })
                        except Exception as e:
                            logger.error("Research sub-agent error: %s", e)
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": f"Research failed: {e}",
                                "is_error": True,
                            })
                    elif block.type == "tool_use" and block.name == "web_search":
                        try:
                            yield f"data: {json.dumps({'type': 'text', 'content': '\\n\\n*Searching the web...*\\n\\n'})}\n\n"
                            search_results = await _web_search(
                                block.input.get("query", ""),
                                block.input.get("count", 5),
                            )
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": search_results,
                            })
                        except Exception as e:
                            logger.error("Web search error: %s", e)
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": f"Search failed: {e}",
                                "is_error": True,
                            })
                    elif block.type == "tool_use" and block.name == "web_fetch":
                        try:
                            yield f"data: {json.dumps({'type': 'text', 'content': '\\n\\n*Reading web page...*\\n\\n'})}\n\n"
                            page_content = await _web_fetch(block.input.get("url", ""))
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": page_content,
                            })
                        except Exception as e:
                            logger.error("Web fetch error: %s", e)
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": f"Fetch failed: {e}",
                                "is_error": True,
                            })
                    elif block.type == "tool_use" and block.name == "save_file":
                        # Create the file
                        try:
                            from app.database import async_session

                            inp = block.input
                            word_count = len(inp.get("content", "").split())

                            # Get next sort order
                            async with async_session() as file_db:
                                count_result = await file_db.execute(
                                    select(WritingFile)
                                    .where(
                                        WritingFile.session_id == session_id_val,
                                        WritingFile.wave == current_wave,
                                    )
                                )
                                existing = count_result.scalars().all()
                                next_sort = len(existing)

                                new_file = WritingFile(
                                    session_id=session_id_val,
                                    wave=current_wave,
                                    file_type=inp.get("file_type", "notes"),
                                    chapter_number=inp.get("chapter_number"),
                                    title=inp["title"],
                                    content=inp["content"],
                                    word_count=word_count,
                                    sort_order=next_sort,
                                )
                                file_db.add(new_file)
                                await file_db.commit()
                                await file_db.refresh(new_file)
                                file_id = str(new_file.id)
                                created_file_ids.append(file_id)

                            # Notify frontend of file creation
                            yield f"data: {json.dumps({'type': 'file_created', 'file': {'id': file_id, 'title': inp['title'], 'file_type': inp.get('file_type', 'notes'), 'chapter_number': inp.get('chapter_number'), 'wave': current_wave, 'word_count': word_count, 'sort_order': next_sort}})}\n\n"

                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": f"File saved: '{inp['title']}' ({word_count} words)",
                            })
                        except Exception as e:
                            logger.error("Failed to save file: %s", e)
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": f"Error saving file: {e}",
                                "is_error": True,
                            })

                # If no tool_use, we're done
                if response.stop_reason != "tool_use":
                    break

                # Continue conversation with tool results
                conv_messages.append({"role": "assistant", "content": response.content})
                conv_messages.append({"role": "user", "content": tool_results})

        except Exception as e:
            logger.error("Claude API error: %s: %s", type(e).__name__, e, exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'content': f'{type(e).__name__}: {e}'})}\n\n"
            return
        finally:
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        # Save assistant message
        try:
            from app.database import async_session

            async with async_session() as save_db:
                assistant_msg = WritingMessage(
                    session_id=session_id_val,
                    wave=current_wave,
                    role="assistant",
                    content=full_text_response,
                    files_generated=created_file_ids,
                    tokens_used=total_tokens,
                )
                save_db.add(assistant_msg)
                await save_db.execute(
                    update(WritingSession)
                    .where(WritingSession.id == session_id_val)
                    .values(total_tokens_used=WritingSession.total_tokens_used + total_tokens)
                )
                await save_db.commit()
        except Exception as e:
            logger.error("Failed to save assistant message: %s", e)

    return StreamingResponse(stream(), media_type="text/event-stream")


# --- Wave advancement ---


@router.post("/sessions/{session_id}/advance")
async def advance_wave(
    session_id: str,
    account: Account = Depends(require_ide_session),
    db: AsyncSession = Depends(get_db),
):
    """Advance to the next wave."""
    session = await _load_session(session_id, account, db)
    new_wave = session.current_wave + 1
    wave_state = dict(session.wave_state or {})
    wave_state[str(session.current_wave)] = {"status": "complete"}
    wave_state[str(new_wave)] = {"status": "in_progress"}

    await db.execute(
        update(WritingSession)
        .where(WritingSession.id == session.id)
        .values(current_wave=new_wave, wave_state=wave_state)
    )
    await db.commit()
    return {"current_wave": new_wave, "wave_state": wave_state}


# --- Publish ---


class PublishRequest(BaseModel):
    format: str = "post"
    authors: list[dict] = []
    tags: list[str] = []
    description: str | None = None


@router.post("/sessions/{session_id}/publish")
async def publish_session(
    session_id: str,
    body: PublishRequest,
    account: Account = Depends(require_ide_session),
    db: AsyncSession = Depends(get_db),
):
    """Publish a writing session as a book on lightpaper.org."""
    session = await _load_session(session_id, account, db)

    if session.published_book_id:
        raise HTTPException(status_code=400, detail="Session already published")

    # Get the latest draft/edited files as chapters
    result = await db.execute(
        select(WritingFile)
        .where(
            WritingFile.session_id == session_id,
            WritingFile.file_type.in_(["draft", "edited"]),
            WritingFile.chapter_number.is_not(None),
        )
        .order_by(WritingFile.chapter_number, WritingFile.wave.desc())
    )
    all_files = result.scalars().all()

    if not all_files:
        raise HTTPException(
            status_code=400,
            detail="No chapter drafts found. Complete at least Wave 4 before publishing.",
        )

    # Deduplicate: take the highest-wave version of each chapter
    chapters_by_num: dict[int, WritingFile] = {}
    for f in all_files:
        if f.chapter_number not in chapters_by_num:
            chapters_by_num[f.chapter_number] = f

    chapters = [chapters_by_num[n] for n in sorted(chapters_by_num.keys())]

    if not chapters:
        raise HTTPException(status_code=400, detail="No chapters found to publish")

    # Build the PublishBookRequest and call the books route internally
    from app.auth import AuthResult
    from app.schemas import AuthorInfo, ChapterInput, PublishBookRequest, PublishOptions

    authors = body.authors or [{"name": account.display_name or account.handle, "handle": account.handle}]
    author_infos = [AuthorInfo(name=a.get("name", ""), handle=a.get("handle")) for a in authors]

    chapter_inputs = [
        ChapterInput(
            title=ch.title,
            content=ch.content,
        )
        for ch in chapters
    ]

    book_request = PublishBookRequest(
        title=session.title,
        subtitle=body.description,
        description=body.description,
        format=body.format,
        authors=author_infos,
        chapters=chapter_inputs,
        tags=body.tags,
        options=PublishOptions(listed=True),
    )

    # Import and call the publish_book logic directly
    from app.routes.books import publish_book

    # Create a mock auth result
    auth_result = AuthResult(account=account, gravity_level=account.gravity_level)

    # We need a real Request object for rate limiting - create the book via the internal function
    # Instead, let's use the book creation logic directly
    from app.id_gen import generate_book_id, generate_doc_id
    from app.models import Book, BookChapter, Document, DocumentVersion
    from app.services.quality import score_book_quality, score_quality
    from app.services.renderer import (
        compute_content_hash,
        compute_reading_time,
        compute_word_count,
        extract_toc,
        render_markdown,
    )
    from app.services.slug import ensure_unique_book_slug, ensure_unique_slug, generate_slug

    book_id = generate_book_id()
    book_slug = generate_slug(session.title)
    book_slug = await ensure_unique_book_slug(book_slug, db)

    chapter_qualities = []
    chapter_data = []
    total_word_count = 0

    for i, ch in enumerate(chapters, 1):
        word_count = compute_word_count(ch.content)
        quality = score_quality(ch.title, ch.content)
        rendered_html = render_markdown(ch.content)
        content_hash = compute_content_hash(ch.content)
        reading_time = compute_reading_time(word_count)
        toc = extract_toc(ch.content)

        chapter_slug = generate_slug(f"{session.title} ch{i} {ch.title}")
        chapter_slug = await ensure_unique_slug(chapter_slug, db)

        chapter_qualities.append((word_count, quality))
        total_word_count += word_count

        chapter_data.append({
            "doc_id": generate_doc_id(),
            "slug": chapter_slug,
            "title": ch.title,
            "content": ch.content,
            "rendered_html": rendered_html,
            "content_hash": content_hash,
            "word_count": word_count,
            "reading_time": reading_time,
            "toc": toc,
            "quality": quality,
            "chapter_number": i,
        })

    book_quality = score_book_quality(chapter_qualities)

    book = Book(
        id=book_id,
        account_id=account.id,
        slug=book_slug,
        title=session.title,
        subtitle=body.description,
        description=body.description,
        format=body.format,
        authors=[a.model_dump() for a in author_infos],
        tags=body.tags,
        listed=True,
        quality_score=book_quality.total,
        quality_detail={
            "structure": book_quality.structure,
            "substance": book_quality.substance,
            "tone": book_quality.tone,
            "attribution": book_quality.attribution,
        },
        author_gravity=account.gravity_level,
        chapter_count=len(chapters),
        total_word_count=total_word_count,
    )
    db.add(book)

    chapter_responses = []
    for cd in chapter_data:
        doc = Document(
            id=cd["doc_id"],
            account_id=account.id,
            slug=cd["slug"],
            title=cd["title"],
            format=body.format,
            authors=[a.model_dump() for a in author_infos],
            tags=body.tags,
            listed=True,
            quality_score=cd["quality"].total,
            quality_detail={
                "structure": cd["quality"].structure,
                "substance": cd["quality"].substance,
                "tone": cd["quality"].tone,
                "attribution": cd["quality"].attribution,
            },
            author_gravity=account.gravity_level,
            book_id=book_id,
        )
        db.add(doc)

        version = DocumentVersion(
            document_id=cd["doc_id"],
            version=1,
            content=cd["content"],
            content_hash=cd["content_hash"],
            rendered_html=cd["rendered_html"],
            word_count=cd["word_count"],
            reading_time=cd["reading_time"],
            toc=cd["toc"],
        )
        db.add(version)

        book_chapter = BookChapter(
            book_id=book_id,
            document_id=cd["doc_id"],
            chapter_number=cd["chapter_number"],
            chapter_title=cd["title"],
        )
        db.add(book_chapter)

        chapter_responses.append({
            "chapter_number": cd["chapter_number"],
            "title": cd["title"],
            "url": f"{settings.base_url}/{cd['slug']}",
            "quality_score": cd["quality"].total,
        })

    # Update session
    await db.execute(
        update(WritingSession)
        .where(WritingSession.id == session.id)
        .values(published_book_id=book_id, status="completed")
    )

    await db.commit()

    book_url = f"{settings.base_url}/{book_slug}"

    return {
        "book_id": book_id,
        "url": book_url,
        "quality_score": book_quality.total,
        "chapter_count": len(chapters),
        "total_word_count": total_word_count,
        "chapters": chapter_responses,
    }


# --- Web search & fetch ---


async def _web_search(query: str, count: int = 5) -> str:
    """Search the web using Brave Search API."""
    import httpx

    if not settings.brave_search_api_key:
        return "Web search not configured. BRAVE_SEARCH_API_KEY is not set."

    count = min(max(count, 1), 10)
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            "https://api.search.brave.com/res/v1/web/search",
            params={"q": query, "count": count},
            headers={
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": settings.brave_search_api_key,
            },
        )
        resp.raise_for_status()
        data = resp.json()

    results = []
    for item in data.get("web", {}).get("results", [])[:count]:
        title = item.get("title", "")
        url = item.get("url", "")
        description = item.get("description", "")
        results.append(f"**{title}**\n{url}\n{description}")

    if not results:
        return f"No results found for: {query}"

    return f"Search results for: {query}\n\n" + "\n\n---\n\n".join(results)


async def _web_fetch(url: str) -> str:
    """Fetch a web page and extract text content."""
    import re

    import httpx

    # Basic URL validation
    if not url.startswith(("http://", "https://")):
        return "Invalid URL. Must start with http:// or https://"

    async with httpx.AsyncClient(
        timeout=20,
        follow_redirects=True,
        headers={"User-Agent": "lightpaper-research/1.0 (https://lightpaper.org)"},
    ) as client:
        resp = await client.get(url)
        resp.raise_for_status()

    content_type = resp.headers.get("content-type", "")
    if "text/html" not in content_type and "text/plain" not in content_type:
        return f"Cannot read this content type: {content_type}"

    html = resp.text

    # Extract title
    title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    title = title_match.group(1).strip() if title_match else ""

    # Remove script, style, nav, header, footer elements
    for tag in ["script", "style", "nav", "header", "footer", "aside", "noscript"]:
        html = re.sub(rf"<{tag}[^>]*>.*?</{tag}>", "", html, flags=re.IGNORECASE | re.DOTALL)

    # Try to extract main/article content first
    main_match = re.search(
        r"<(?:main|article)[^>]*>(.*?)</(?:main|article)>",
        html, re.IGNORECASE | re.DOTALL,
    )
    text_html = main_match.group(1) if main_match else html

    # Convert common block elements to newlines
    text_html = re.sub(r"<(?:p|div|br|h[1-6]|li|tr)[^>]*>", "\n", text_html, flags=re.IGNORECASE)

    # Strip all remaining HTML tags
    text = re.sub(r"<[^>]+>", "", text_html)

    # Clean up whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()

    # Truncate to ~15k chars to fit in context
    if len(text) > 15000:
        text = text[:15000] + "\n\n[...truncated]"

    header = f"# {title}\nSource: {url}\n\n" if title else f"Source: {url}\n\n"
    return header + text


# --- Research sub-agent ---


async def _run_research(client, query: str, context: str, session_id: str) -> str:
    """Spawn a focused research sub-agent to investigate a topic."""
    research_prompt = f"""You are a research assistant for a book being written on lightpaper.org.

Investigate the following topic thoroughly and return a detailed research brief.

RESEARCH QUERY: {query}

CONTEXT FROM MANUSCRIPT: {context or 'No additional context provided.'}

Your research brief should include:
- Key facts, dates, and details
- Multiple perspectives or interpretations where relevant
- Specific details that would make fiction feel authentic or non-fiction feel authoritative
- Sources of potential inaccuracy to watch out for
- Vivid sensory or experiential details a writer could use

Be thorough but concise. Focus on what's most useful for the manuscript."""

    response = await client.messages.create(
        model="claude-opus-4-6",
        max_tokens=8000,
        thinking={
            "type": "enabled",
            "budget_tokens": 8000,
        },
        messages=[{"role": "user", "content": research_prompt}],
    )

    # Extract text from response (skip thinking blocks)
    text_parts = []
    for block in response.content:
        if block.type == "text":
            text_parts.append(block.text)
    return "\n".join(text_parts) or "No research results."


# --- Helpers ---


async def _load_session(session_id: str, account: Account, db: AsyncSession) -> WritingSession:
    result = await db.execute(
        select(WritingSession).where(
            WritingSession.id == session_id,
            WritingSession.account_id == account.id,
            WritingSession.deleted_at.is_(None),
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


async def _load_files(session_id: str, db: AsyncSession) -> list[dict]:
    result = await db.execute(
        select(WritingFile)
        .where(WritingFile.session_id == session_id)
        .order_by(WritingFile.wave, WritingFile.sort_order)
    )
    files = result.scalars().all()
    return [
        {
            "id": str(f.id),
            "wave": f.wave,
            "file_type": f.file_type,
            "chapter_number": f.chapter_number,
            "title": f.title,
            "word_count": f.word_count,
            "sort_order": f.sort_order,
        }
        for f in files
    ]
