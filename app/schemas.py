"""Pydantic request/response schemas for lightpaper.org API."""

from datetime import datetime
from pydantic import BaseModel, Field


# --- Publish ---

class AuthorInfo(BaseModel):
    name: str
    handle: str | None = None


class PublishOptions(BaseModel):
    slug: str | None = None
    listed: bool = True
    og_image: str = "auto"


class PublishRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    subtitle: str | None = None
    content: str = Field(..., min_length=1)
    format: str = "markdown"
    authors: list[AuthorInfo] = []
    metadata: dict = {}
    options: PublishOptions = PublishOptions()


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
    title: str | None = None
    subtitle: str | None = None
    content: str | None = None
    authors: list[AuthorInfo] | None = None
    metadata: dict | None = None
    tags: list[str] | None = None
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
    created_at: datetime


class AccountCreateRequest(BaseModel):
    handle: str | None = None
    display_name: str | None = None


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


# --- Errors ---

class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None
