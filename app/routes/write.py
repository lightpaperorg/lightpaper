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


# --- Chat (streaming with tool_use for file creation) ---

# Tool definition for Claude to create files
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
            max_turns = 5  # Prevent infinite tool_use loops

            for _ in range(max_turns):
                response = await client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=8192,
                    system=system_prompt,
                    messages=conv_messages,
                    tools=[SAVE_FILE_TOOL],
                )

                total_tokens += response.usage.input_tokens + response.usage.output_tokens

                # Process content blocks
                tool_results = []
                for block in response.content:
                    if block.type == "text":
                        full_text_response += block.text
                        yield f"data: {json.dumps({'type': 'text', 'content': block.text})}\n\n"
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
            logger.error("Claude API error: %s", e)
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
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
