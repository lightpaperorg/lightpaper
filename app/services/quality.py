"""Deterministic quality scoring (0-100). No LLM, <100ms."""

import re
from dataclasses import dataclass


@dataclass
class QualityResult:
    structure: int  # 0-25
    substance: int  # 0-25
    tone: int  # 0-25
    attribution: int  # 0-25
    total: int  # 0-100
    suggestions: list[str]


CLICKBAIT_PATTERNS = [
    r"you won't believe",
    r"this one trick",
    r"doctors hate",
    r"number \d+ will shock",
    r"mind.?blowing",
    r"game.?changer",
    r"revolutionary",
    r"insane",
]


def score_quality(title: str, content: str) -> QualityResult:
    suggestions = []

    # --- Structure (0-25) ---
    headings = re.findall(r"^#{1,6}\s", content, re.MULTILINE)
    heading_count = len(headings)
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip() and not p.strip().startswith("#")]
    para_count = len(paragraphs)

    structure = 0
    # Heading hierarchy
    if heading_count >= 3:
        structure += 10
    elif heading_count >= 1:
        structure += 5
    else:
        suggestions.append("Add section headings to improve structure")

    # Section variety
    if para_count >= 8:
        structure += 8
    elif para_count >= 4:
        structure += 5
    elif para_count >= 2:
        structure += 3
    else:
        suggestions.append("Break content into more paragraphs")

    # Paragraph length variety (not all the same length)
    if para_count >= 3:
        lengths = [len(p.split()) for p in paragraphs[:10]]
        length_variance = max(lengths) - min(lengths) if lengths else 0
        if length_variance > 20:
            structure += 7
        elif length_variance > 10:
            structure += 5
        else:
            structure += 3

    structure = min(25, structure)

    # --- Substance (0-25) ---
    words = content.split()
    word_count = len(words)

    substance = 0
    if word_count >= 2000:
        substance += 12
    elif word_count >= 1000:
        substance += 10
    elif word_count >= 500:
        substance += 7
    elif word_count >= 300:
        substance += 5
    else:
        suggestions.append("Add more content (minimum 300 words for quality indexing)")

    # Code blocks (information density signal)
    code_blocks = len(re.findall(r"```", content))
    if code_blocks >= 4:
        substance += 5
    elif code_blocks >= 2:
        substance += 3

    # Lists (structured information)
    list_items = len(re.findall(r"^[\-\*]\s", content, re.MULTILINE))
    if list_items >= 5:
        substance += 4
    elif list_items >= 2:
        substance += 2

    # Tables
    tables = len(re.findall(r"^\|.+\|", content, re.MULTILINE))
    if tables >= 3:
        substance += 4
    elif tables >= 1:
        substance += 2

    substance = min(25, substance)

    # --- Tone (0-25) ---
    tone = 18  # professional baseline

    # Clickbait penalty
    full_text = (title + " " + content).lower()
    clickbait_hits = sum(1 for p in CLICKBAIT_PATTERNS if re.search(p, full_text))
    tone -= clickbait_hits * 4

    # Exclamation density
    exclamation_count = content.count("!")
    sentences = len(re.findall(r"[.!?]+", content))
    if sentences > 0 and exclamation_count / max(sentences, 1) > 0.3:
        tone -= 5
        suggestions.append("Reduce exclamation marks for a more professional tone")

    # ALL CAPS words penalty (more than 3 in a row)
    caps_runs = re.findall(r"\b[A-Z]{4,}\b", content)
    if len(caps_runs) > 3:
        tone -= 3

    tone = max(0, min(25, tone))

    # --- Attribution (0-25) ---
    attribution = 0

    # External links
    links = re.findall(r"\[([^\]]+)\]\(https?://[^)]+\)", content)
    if len(links) >= 5:
        attribution += 10
    elif len(links) >= 2:
        attribution += 7
    elif len(links) >= 1:
        attribution += 4
    else:
        suggestions.append("Add external references to improve attribution score")

    # References/bibliography section
    if re.search(r"^#{1,3}\s*(references|bibliography|sources|works cited)", content, re.MULTILINE | re.IGNORECASE):
        attribution += 8
    else:
        suggestions.append("Add a References section")

    # Footnotes
    footnotes = len(re.findall(r"\[\^\d+\]", content))
    if footnotes >= 3:
        attribution += 7
    elif footnotes >= 1:
        attribution += 4

    attribution = min(25, attribution)

    total = structure + substance + tone + attribution

    return QualityResult(
        structure=structure,
        substance=substance,
        tone=tone,
        attribution=attribution,
        total=total,
        suggestions=suggestions,
    )
