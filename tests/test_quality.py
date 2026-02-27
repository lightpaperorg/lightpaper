"""Test quality scoring service."""

from app.services.quality import score_quality


def _make_content(word_count: int = 500, headings: int = 3, links: int = 0) -> str:
    """Generate test content with specified characteristics."""
    sections = []
    for i in range(headings):
        sections.append(f"## Section {i + 1}")
        words_per_section = word_count // max(headings, 1)
        sections.append(" ".join(["word"] * words_per_section))
    if links:
        sections.append("## References")
        for j in range(links):
            sections.append(f"[Reference {j+1}](https://example.com/{j+1})")
    return "\n\n".join(sections)


def test_minimal_content_low_score():
    """300 words, no headings = low structure score."""
    content = " ".join(["word"] * 300)
    result = score_quality("Test", content)
    assert result.total < 50
    assert result.structure < 10


def test_well_structured_content():
    """500+ words, multiple headings, links = decent score."""
    content = _make_content(word_count=800, headings=4, links=3)
    result = score_quality("A Well-Structured Document", content)
    assert result.total >= 40
    assert result.structure >= 10


def test_high_quality_content():
    """2000+ words, many headings, code blocks, references = high score."""
    content = _make_content(word_count=2000, headings=6, links=5)
    content += "\n\n```python\ndef example():\n    return True\n```\n\n```python\ndef another():\n    pass\n```"
    content += "\n\n## References\n\n[^1]: First reference\n[^2]: Second reference\n[^3]: Third reference"
    result = score_quality("Comprehensive Technical Analysis", content)
    assert result.total >= 55
    assert result.substance >= 10


def test_clickbait_penalty():
    """Clickbait phrases reduce tone score."""
    content = _make_content(word_count=500, headings=3)
    clean = score_quality("Normal Title", content)

    clickbait_content = content + "\n\nYou won't believe what happened next! This is mind-blowing!"
    clickbait = score_quality("You Won't Believe This One Trick", clickbait_content)

    assert clickbait.tone < clean.tone


def test_suggestions_generated():
    """Suggestions are generated for missing elements."""
    content = " ".join(["word"] * 300)
    result = score_quality("Test", content)
    assert len(result.suggestions) > 0


def test_score_bounds():
    """All scores are within bounds."""
    content = _make_content(word_count=1000, headings=5, links=3)
    result = score_quality("Test Document", content)
    assert 0 <= result.structure <= 25
    assert 0 <= result.substance <= 25
    assert 0 <= result.tone <= 25
    assert 0 <= result.attribution <= 25
    assert 0 <= result.total <= 100
