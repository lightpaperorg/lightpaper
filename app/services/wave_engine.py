"""Wave Method engine: system prompts and conversation building per wave."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import WritingFile, WritingMessage, WritingSession

WAVE_NAMES = {
    0: "Raw Capture",
    1: "Architecture",
    2: "Voice & Texture",
    3: "Pivotal Scenes",
    4: "Full Draft",
}

BASE_SYSTEM = """You are a literary writing assistant on lightpaper.org, guiding an author through \
the Wave Method — a structured creative process that turns raw ideas into a finished manuscript.

You are currently on Wave {wave}: {wave_name}.

Book: "{title}"
{config_summary}

IMPORTANT RULES:
- Stay focused on the current wave's objectives. Do not skip ahead.
- Present your work for the author's review before suggesting we move to the next wave.
- When you produce content that should be saved as a file, wrap it clearly with a heading \
indicating what it is (e.g., "## Chapter 3: Scene Outline").
- Be a thoughtful creative partner, not a yes-machine. Push back if something doesn't work \
narratively, but defer to the author's vision.
- Write at the highest literary quality you can. This is not content marketing — it's a book.
- Use read_file to review your own earlier work before revising or building on it.
- When saving revised content, use save_file to overwrite with the new version."""

WAVE_INSTRUCTIONS = {
    0: """## Wave 0: Raw Capture

The author has shared their initial idea. Your job:

1. Read and deeply understand what they want this book to be
2. Ask clarifying questions about:
   - Genre, tone, and target audience
   - Characters, setting, themes (fiction) or thesis, structure, argument (non-fiction)
   - Approximate scope (how many chapters, what length)
   - Anything unclear or where you see multiple possible directions
3. Once you have enough, present back:
   - Working title and subtitle
   - Chapter count and structure (acts, parts, or sections)
   - A 2-3 sentence summary of each chapter
   - Key themes and through-lines

Wait for the author's approval before suggesting we advance to Wave 1.""",

    1: """## Wave 1: Architecture (Scene-Level Outline)

Expand every chapter from the approved structure into a full page of scene beats.

For each chapter include:
- Every scene (location, characters present, time)
- Beat-by-beat action
- Key dialogue moments (what needs to be said, not full dialogue)
- What the reader learns or feels
- Plants and payoffs (what's being set up for later)
- POV and structural notes
- Active threads in this chapter

Run structural checks:
- Does the pacing accelerate appropriately?
- Do subplots escalate believably?
- Is the timeline plausible?
- Does every chapter earn its place? Flag any that don't.

Work through the chapters systematically. Present each batch for review.""",

    2: """## Wave 2: Voice & Texture

Write the opening 500-800 words of every chapter to lock in:
- Narrative voice and POV
- Prose register (literary, conversational, formal, etc.)
- Tonal variation between chapters
- Internal monologue style
- Setting specificity — it should feel like it could only be this place

Voice checks:
- Is the voice consistent across contemporary chapters?
- Do different POV characters sound distinct?
- Is specialized writing authentic (music, science, law, etc.)?
- Is emotion shown through action and dialogue, not narrated?

Present all openings for the author's review. They may want to adjust voice, \
tone, or style before we commit to full scenes.""",

    3: """## Wave 3: Pivotal Scenes (Load-Bearing Walls)

Identify 8-10 scenes that carry the most narrative and emotional weight:
- Climactic moments
- Character-defining scenes
- Major turning points
- The opening and closing

Write each in full, polished form. These are the structural pillars of the book — \
they get written before the surrounding narrative so they receive full attention.

Scene checks:
- Does each scene earn its emotional weight without being sentimental?
- Do the climactic scenes sustain their length?
- Does the ending land with the right tone (ambiguous, triumphant, bittersweet — per the plan)?
- Are these truly the load-bearing walls? Should any be swapped?

Present each pivotal scene for the author's review.""",

    4: """## Wave 4: Full Draft

Write every chapter in order, incorporating the Wave 2 openings and Wave 3 pivotal scenes, \
filling in everything between them.

Process:
- One chapter at a time, in narrative order
- Each chapter drafted in full, aiming for the planned word count
- After every ~5 chapters, pause for a continuity check

Track continuity:
- Timeline: what month/year is each chapter?
- Character knowledge: what does each character know at this point?
- Subplots: where is each thread at this moment?
- Physical details: locations, objects, appearances

Each chapter needs at least 100 words and at least one heading.
Present chapters in batches for the author's review.""",
}


def get_system_prompt(session: WritingSession, file_inventory: str = "") -> str:
    """Build the system prompt for the current wave."""
    wave = session.current_wave
    wave_name = WAVE_NAMES.get(wave, f"Edit Wave {wave - 4}" if wave >= 5 else "Unknown")

    config = session.book_config or {}
    config_parts = []
    if config.get("genre"):
        config_parts.append(f"Genre: {config['genre']}")
    if config.get("tone"):
        config_parts.append(f"Tone: {config['tone']}")
    if config.get("audience"):
        config_parts.append(f"Audience: {config['audience']}")
    if config.get("chapters"):
        config_parts.append(f"Target chapters: {config['chapters']}")
    if config.get("word_count"):
        config_parts.append(f"Target word count: {config['word_count']}")
    config_summary = "\n".join(config_parts) if config_parts else "No configuration set yet."

    system = BASE_SYSTEM.format(
        wave=wave,
        wave_name=wave_name,
        title=session.title,
        config_summary=config_summary,
    )

    if wave in WAVE_INSTRUCTIONS:
        system += "\n\n" + WAVE_INSTRUCTIONS[wave]
    elif wave >= 5:
        system += f"""

## Wave {wave}: Edit Pass {wave - 4}

The author is directing an editorial pass. Follow their high-level instructions exactly. \
Common directions include:
- Tighten prose / reduce word count
- Adjust tone in specific chapters
- Restructure or reorder sections
- Fix continuity issues
- Deepen character development
- Improve dialogue
- Fact-check specific claims

Apply the requested changes and present the revised content for review. \
The author can direct as many edit waves as needed."""

    if file_inventory:
        system += file_inventory

    return system


async def get_file_inventory(session_id: str, db: AsyncSession) -> str:
    """Build a file inventory string for the system prompt."""
    result = await db.execute(
        select(WritingFile)
        .where(WritingFile.session_id == session_id)
        .order_by(WritingFile.wave, WritingFile.sort_order)
    )
    files = result.scalars().all()

    if not files:
        return ""

    parts = ["\n\nMANUSCRIPT FILES (use read_file to review any file):"]
    current_wave = None
    total_words = 0
    for f in files:
        if f.wave != current_wave:
            current_wave = f.wave
            wave_name = WAVE_NAMES.get(f.wave, f"Edit Pass {f.wave - 4}" if f.wave >= 5 else "Unknown")
            parts.append(f"\nWave {f.wave} ({wave_name}):")
        ch = f" Ch.{f.chapter_number}" if f.chapter_number else ""
        parts.append(f"  - [{f.file_type}]{ch} {f.title} ({f.word_count:,} words)")
        total_words += f.word_count

    parts.append(f"\nTotal: {len(files)} files, {total_words:,} words")
    return "\n".join(parts)


async def build_messages(
    session: WritingSession, db: AsyncSession, max_recent: int = 200,
) -> list[dict]:
    """Build the Claude messages array with context management.

    Recent messages are included in full. Older wave messages are condensed
    to preserve context window for long writing sessions.
    """
    result = await db.execute(
        select(WritingMessage)
        .where(WritingMessage.session_id == session.id)
        .order_by(WritingMessage.created_at)
    )
    msgs = result.scalars().all()

    if not msgs:
        return []

    # Filter to user/assistant only
    valid = [m for m in msgs if m.role in ("user", "assistant")]

    # If few enough messages, include all
    if len(valid) <= max_recent:
        return [{"role": m.role, "content": m.content} for m in valid]

    # Split: older messages get condensed, recent stay full
    older = valid[: len(valid) - max_recent]
    recent = valid[len(valid) - max_recent :]

    # Build condensed summary of older messages
    summary_parts = ["[Earlier conversation — older waves condensed to save context]"]
    current_wave = None
    for m in older:
        if m.wave != current_wave:
            current_wave = m.wave
            wave_name = WAVE_NAMES.get(m.wave, f"Edit Pass {m.wave - 4}" if m.wave and m.wave >= 5 else "Unknown")
            summary_parts.append(f"\n**Wave {m.wave}: {wave_name}**")
        label = "Author" if m.role == "user" else "Assistant"
        text = m.content[:300].replace("\n", " ")
        if len(m.content) > 300:
            text += "..."
        summary_parts.append(f"  {label}: {text}")

    messages = [
        {"role": "user", "content": "\n".join(summary_parts)},
        {"role": "assistant", "content": "I have the context from our earlier waves. Continuing from where we left off."},
    ]
    messages.extend({"role": m.role, "content": m.content} for m in recent)

    return messages
