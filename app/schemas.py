"""Pydantic request/response schemas for lightpaper.org API."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

# --- Publish ---


class AuthorInfo(BaseModel):
    name: str = Field(..., max_length=200)
    handle: str | None = Field(None, max_length=100)


class PublishOptions(BaseModel):
    slug: str | None = Field(None, max_length=80)
    listed: bool = True
    og_image: str = "auto"


class PublishRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    subtitle: str | None = Field(None, max_length=1000)
    content: str = Field(..., min_length=1, max_length=500_000)
    format: Literal["paper", "essay", "post", "markdown", "academic", "report", "tutorial"] = "post"
    authors: list[AuthorInfo] = Field(default_factory=list, max_length=20)
    metadata: dict = Field(default_factory=dict)
    options: PublishOptions = PublishOptions()
    tags: list[str] = Field(default_factory=list, max_length=50)

    @field_validator("metadata")
    @classmethod
    def validate_metadata(cls, v: dict) -> dict:
        """Prevent deeply nested or oversized metadata."""
        import json

        serialized = json.dumps(v)
        if len(serialized) > 50_000:
            raise ValueError("metadata must be less than 50KB when serialized")
        return v


class QualityBreakdown(BaseModel):
    structure: int
    substance: int
    tone: int
    attribution: int


class PublishResponse(BaseModel):
    id: str
    url: str
    permanent_url: str
    version: int
    created_at: datetime
    word_count: int
    reading_time_minutes: int
    content_hash: str
    quality_score: int
    quality_breakdown: QualityBreakdown
    quality_suggestions: list[str]
    author_gravity: int
    author_gravity_badges: list[str]
    gravity_note: str | None = None


# --- Documents ---


class DocumentResponse(BaseModel):
    id: str
    title: str
    subtitle: str | None
    content: str
    format: str
    slug: str | None
    authors: list[AuthorInfo]
    metadata: dict
    tags: list[str]
    word_count: int | None
    reading_time_minutes: int | None
    quality_score: int | None
    author_gravity: int
    current_version: int
    listed: bool
    created_at: datetime
    updated_at: datetime
    permanent_url: str
    url: str | None


class DocumentUpdateRequest(BaseModel):
    title: str | None = Field(None, max_length=500)
    subtitle: str | None = Field(None, max_length=1000)
    content: str | None = Field(None, max_length=500_000)
    format: Literal["paper", "essay", "post", "markdown", "academic", "report", "tutorial"] | None = None
    authors: list[AuthorInfo] | None = Field(None, max_length=20)
    metadata: dict | None = None
    tags: list[str] | None = Field(None, max_length=50)
    listed: bool | None = None


class VersionResponse(BaseModel):
    version: int
    content_hash: str
    word_count: int | None
    reading_time: int | None
    created_at: datetime


# --- Search ---


class SearchResult(BaseModel):
    id: str
    title: str
    subtitle: str | None
    url: str
    authors: list[AuthorInfo]
    tags: list[str]
    quality_score: int | None
    word_count: int | None
    created_at: datetime
    snippet: str | None = None


class SearchResponse(BaseModel):
    results: list[SearchResult]
    total: int
    limit: int
    offset: int


# --- Accounts ---


class AccountResponse(BaseModel):
    id: str
    handle: str | None
    display_name: str | None
    email: str | None
    bio: str | None
    tier: str
    gravity_level: int
    gravity_badges: list[str]
    verified_domain: str | None
    verified_linkedin: bool
    orcid_id: str | None
    linkedin_url: str | None = None
    created_at: datetime


class AccountCreateRequest(BaseModel):
    handle: str | None = None
    display_name: str | None = None


class AccountUpdateRequest(BaseModel):
    display_name: str | None = Field(None, max_length=200)
    bio: str | None = Field(None, max_length=2000)
    linkedin_url: str | None = Field(None, max_length=500)


# --- API Keys ---


class KeyCreateRequest(BaseModel):
    label: str | None = None
    tier: str = "free"


class KeyResponse(BaseModel):
    prefix: str
    label: str | None
    tier: str
    created_at: datetime


class KeyCreateResponse(BaseModel):
    key: str  # full key — shown only once
    prefix: str
    label: str | None
    tier: str
    created_at: datetime


# --- Verification ---


class DomainVerifyRequest(BaseModel):
    domain: str


class DomainVerifyResponse(BaseModel):
    domain: str
    txt_record: str
    instructions: str


class GravityResponse(BaseModel):
    level: int
    badges: list[str]
    next_level: str | None
    multiplier: float
    featured_threshold: int


# --- Auth (Email OTP + LinkedIn OAuth) ---


class AuthEmailRequest(BaseModel):
    email: str = Field(..., max_length=320)
    display_name: str | None = Field(None, max_length=200)
    handle: str | None = Field(None, max_length=100)


class AuthEmailResponse(BaseModel):
    session_id: str
    message: str
    expires_in: int


class AuthVerifyRequest(BaseModel):
    session_id: str
    code: str = Field(..., min_length=6, max_length=6)


class AuthVerifyResponse(BaseModel):
    account_id: str
    handle: str | None
    api_key: str
    is_new_account: bool
    gravity_level: int
    next_level: str | None


class LinkedInAuthStartResponse(BaseModel):
    authorization_url: str
    session_id: str
    instructions: str


class LinkedInAuthPollResponse(BaseModel):
    completed: bool
    account_id: str | None = None
    handle: str | None = None
    api_key: str | None = None
    gravity_level: int | None = None


# --- LinkedIn Verification ---


class LinkedInVerifyResponse(BaseModel):
    authorization_url: str
    state: str
    instructions: str


class LinkedInCheckResponse(BaseModel):
    verified: bool
    gravity_level: int


# --- ORCID Verification ---


class OrcidVerifyRequest(BaseModel):
    orcid_id: str = Field(..., max_length=19)

    @field_validator("orcid_id")
    @classmethod
    def validate_orcid_format(cls, v: str) -> str:
        import re

        if not re.match(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$", v):
            raise ValueError("ORCID iD must be in format 0000-0000-0000-000X")
        return v


class OrcidVerifyResponse(BaseModel):
    verified: bool
    gravity_level: int
    orcid_name: str | None = None


# --- Credentials ---


class CredentialSubmission(BaseModel):
    credential_type: Literal["degree", "certification", "employment"]
    institution: str = Field(..., min_length=1, max_length=500)
    title: str = Field(..., min_length=1, max_length=500)
    year: int | None = Field(None, ge=1900, le=2100)
    evidence_tier: Literal["confirmed", "supported", "claimed"]
    evidence_data: dict = Field(default_factory=dict)
    agent_notes: str | None = Field(None, max_length=2000)

    @field_validator("evidence_data")
    @classmethod
    def validate_evidence_data(cls, v: dict) -> dict:
        import json

        if len(json.dumps(v)) > 50_000:
            raise ValueError("evidence_data must be less than 50KB when serialized")
        return v


class CredentialSubmitRequest(BaseModel):
    credentials: list[CredentialSubmission] = Field(..., min_length=1, max_length=20)


class CredentialResponse(BaseModel):
    id: str
    credential_type: str
    institution: str
    title: str
    year: int | None
    evidence_tier: str
    agent_notes: str | None
    created_at: datetime
    updated_at: datetime


class CredentialSubmitResponse(BaseModel):
    credentials: list[CredentialResponse]
    gravity_level: int
    gravity_badges: list[str]
    credential_points: int


# --- Books ---


class ChapterInput(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    subtitle: str | None = Field(None, max_length=1000)
    content: str = Field(..., min_length=1, max_length=500_000)
    slug: str | None = Field(None, max_length=80)


class PublishBookRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    subtitle: str | None = Field(None, max_length=1000)
    description: str | None = Field(None, max_length=10_000)
    format: Literal["paper", "essay", "post"] = "post"
    authors: list[AuthorInfo] = Field(default_factory=list, max_length=20)
    chapters: list[ChapterInput] = Field(..., min_length=1, max_length=200)
    tags: list[str] = Field(default_factory=list, max_length=50)
    metadata: dict = Field(default_factory=dict)
    options: PublishOptions = PublishOptions()
    cover_image_url: str | None = None

    @field_validator("metadata")
    @classmethod
    def validate_metadata(cls, v: dict) -> dict:
        import json

        if len(json.dumps(v)) > 50_000:
            raise ValueError("metadata must be less than 50KB when serialized")
        return v


class ChapterResponse(BaseModel):
    chapter_number: int
    document_id: str
    title: str
    url: str
    permanent_url: str
    word_count: int
    reading_time_minutes: int
    quality_score: int


class PublishBookResponse(BaseModel):
    id: str
    url: str
    title: str
    chapters: list[ChapterResponse]
    quality_score: int
    quality_breakdown: QualityBreakdown
    total_word_count: int
    chapter_count: int
    author_gravity: int


class BookResponse(BaseModel):
    id: str
    title: str
    subtitle: str | None
    description: str | None
    format: str
    slug: str | None
    authors: list[AuthorInfo]
    tags: list[str]
    cover_image_url: str | None
    quality_score: int | None
    author_gravity: int
    chapter_count: int
    total_word_count: int
    listed: bool
    created_at: datetime
    updated_at: datetime
    url: str | None
    chapters: list[ChapterResponse]


class BookUpdateRequest(BaseModel):
    title: str | None = Field(None, max_length=500)
    subtitle: str | None = Field(None, max_length=1000)
    description: str | None = Field(None, max_length=10_000)
    format: Literal["paper", "essay", "post"] | None = None
    authors: list[AuthorInfo] | None = Field(None, max_length=20)
    slug: str | None = Field(None, max_length=80)
    tags: list[str] | None = Field(None, max_length=50)
    metadata: dict | None = None
    listed: bool | None = None
    cover_image_url: str | None = None


class AddChapterRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    subtitle: str | None = Field(None, max_length=1000)
    content: str = Field(..., min_length=1, max_length=500_000)
    slug: str | None = Field(None, max_length=80)
    position: int | None = Field(None, ge=1, description="Insert at this position (appends if omitted)")


class ReorderChaptersRequest(BaseModel):
    chapter_order: list[str] = Field(..., min_length=1, description="Document IDs in desired order")


# --- Errors ---


class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None
