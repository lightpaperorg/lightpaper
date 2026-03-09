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


# --- Auth endpoints ---


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
                session_token = _sign_token(str(account.id))
                response.set_cookie(
                    key="lp_session",
                    value=session_token,
                    httponly=True,
                    secure=True,
                    samesite="lax",
                    max_age=30 * 86400,
                    path="/",
                )
                return {
                    "handle": account.handle,
                    "display_name": account.display_name,
                    "gravity_level": account.gravity_level,
                }

    raise HTTPException(status_code=401, detail="Invalid API key")


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


# --- Chat (streaming) ---


@router.post("/sessions/{session_id}/chat")
@limiter.limit("30/minute")
async def chat(
    request: Request,
    session_id: str,
    body: ChatRequest,
    account: Account = Depends(require_ide_session),
    db: AsyncSession = Depends(get_db),
):
    """Send a message and get a streaming response from Claude."""
    session = await _load_session(session_id, account, db)

    if not settings.anthropic_api_key:
        raise HTTPException(status_code=503, detail="AI service not configured")

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

    async def stream():
        import anthropic

        client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        full_response = ""
        total_tokens = 0

        try:
            async with client.messages.stream(
                model="claude-sonnet-4-20250514",
                max_tokens=8192,
                system=system_prompt,
                messages=messages,
            ) as stream_resp:
                async for text in stream_resp.text_stream:
                    full_response += text
                    yield f"data: {text}\n\n"

                # Get final usage
                final = await stream_resp.get_final_message()
                total_tokens = final.usage.input_tokens + final.usage.output_tokens

        except Exception as e:
            logger.error("Claude API error: %s", e)
            yield f"data: [ERROR] {str(e)}\n\n"
            return
        finally:
            yield "data: [DONE]\n\n"

        # Save assistant message (after stream completes)
        try:
            from app.database import async_session

            async with async_session() as save_db:
                assistant_msg = WritingMessage(
                    session_id=session.id,
                    wave=session.current_wave,
                    role="assistant",
                    content=full_response,
                    tokens_used=total_tokens,
                )
                save_db.add(assistant_msg)
                await save_db.execute(
                    update(WritingSession)
                    .where(WritingSession.id == session.id)
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
