"""SQLAlchemy ORM models for lightpaper.org."""

from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, FetchedValue, ForeignKey, Integer, Text, text
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR, UUID
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Account(Base):
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    firebase_uid = Column(Text, nullable=True)
    handle = Column(Text, unique=True)
    display_name = Column(Text)
    email = Column(Text)
    bio = Column(Text)
    avatar_url = Column(Text)
    tier = Column(Text, nullable=False, default="free")
    verified_domain = Column(Text)
    verified_linkedin = Column(Boolean, default=False)
    orcid_id = Column(Text)
    linkedin_profile_id = Column(Text)
    linkedin_url = Column(Text)
    gravity_level = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    deleted_at = Column(DateTime(timezone=True))

    api_keys = relationship("ApiKey", back_populates="account", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="account")
    credentials = relationship("Credential", back_populates="account", cascade="all, delete-orphan")


class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    key_hash = Column(Text, unique=True, nullable=False)
    key_prefix = Column(Text, nullable=False)
    tier = Column(Text, nullable=False, default="free")
    label = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    revoked_at = Column(DateTime(timezone=True))

    account = relationship("Account", back_populates="api_keys")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Text, primary_key=True)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"))
    slug = Column(Text, unique=True)
    title = Column(Text, nullable=False)
    subtitle = Column(Text)
    format = Column(Text, nullable=False, default="markdown")
    current_version = Column(Integer, nullable=False, default=1)
    authors = Column(JSONB, default=list)
    doc_metadata = Column("metadata", JSONB, default=dict)
    tags = Column(JSONB, default=list)
    listed = Column(Boolean, default=True)
    quality_score = Column(Integer)
    quality_detail = Column(JSONB)
    author_gravity = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    deleted_at = Column(DateTime(timezone=True))
    google_indexed = Column(Boolean)
    google_index_checked_at = Column(DateTime(timezone=True))
    google_coverage_state = Column(Text)
    search_vector = Column(TSVECTOR, FetchedValue())

    book_id = Column(Text, ForeignKey("books.id", ondelete="SET NULL"))

    account = relationship("Account", back_populates="documents")
    versions = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan")
    book = relationship("Book", back_populates="chapter_docs", foreign_keys=[book_id])


class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_id = Column(Text, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    version = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    content_hash = Column(Text, nullable=False)
    rendered_html = Column(Text)
    word_count = Column(Integer)
    reading_time = Column(Integer)
    toc = Column(JSONB)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))

    document = relationship("Document", back_populates="versions")


class Citation(Base):
    __tablename__ = "citations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    source_doc_id = Column(Text, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    target_doc_id = Column(Text, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))


class DomainVerification(Base):
    __tablename__ = "domain_verifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    domain = Column(Text, nullable=False)
    txt_token = Column(Text, nullable=False)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))


class Credential(Base):
    __tablename__ = "credentials"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    credential_type = Column(Text, nullable=False)  # degree, certification, employment
    institution = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    year = Column(Integer)
    evidence_tier = Column(Text, nullable=False, default="claimed")  # confirmed, supported, claimed
    evidence_data = Column(JSONB, default=dict)
    agent_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))

    account = relationship("Account", back_populates="credentials")


class LinkedInVerification(Base):
    __tablename__ = "linkedin_verifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    state_token = Column(Text, unique=True, nullable=False)
    verified = Column(Boolean, default=False)
    linkedin_profile_id = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))


class EmailAuthSession(Base):
    __tablename__ = "email_auth_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(Text, unique=True, nullable=False)
    email = Column(Text, nullable=False)
    code_hash = Column(Text, nullable=False)
    display_name = Column(Text)
    handle = Column(Text)
    attempts = Column(Integer, nullable=False, default=0)
    max_attempts = Column(Integer, nullable=False, default=5)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    verified_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))


class LinkedInAuthSession(Base):
    __tablename__ = "linkedin_auth_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(Text, unique=True, nullable=False)
    state_token = Column(Text, unique=True, nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"))
    api_key_plain = Column(Text)
    completed_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))


class Book(Base):
    __tablename__ = "books"

    id = Column(Text, primary_key=True)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    slug = Column(Text, unique=True)
    title = Column(Text, nullable=False)
    subtitle = Column(Text)
    description = Column(Text)
    format = Column(Text, nullable=False, default="post")
    authors = Column(JSONB, default=list)
    tags = Column(JSONB, default=list)
    doc_metadata = Column("metadata", JSONB, default=dict)
    cover_image_url = Column(Text)
    listed = Column(Boolean, default=True)
    quality_score = Column(Integer)
    quality_detail = Column(JSONB)
    author_gravity = Column(Integer, nullable=False, default=0)
    chapter_count = Column(Integer, nullable=False, default=0)
    total_word_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    deleted_at = Column(DateTime(timezone=True))
    search_vector = Column(TSVECTOR, FetchedValue())

    account = relationship("Account")
    chapters = relationship("BookChapter", back_populates="book", cascade="all, delete-orphan",
                            order_by="BookChapter.chapter_number")
    chapter_docs = relationship("Document", back_populates="book", foreign_keys="Document.book_id")


class BookChapter(Base):
    __tablename__ = "book_chapters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    book_id = Column(Text, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(Text, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chapter_number = Column(Integer, nullable=False)
    chapter_title = Column(Text)

    book = relationship("Book", back_populates="chapters")
    document = relationship("Document")


class WritingSession(Base):
    __tablename__ = "writing_sessions"

    id = Column(Text, primary_key=True)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    title = Column(Text, nullable=False)
    status = Column(Text, nullable=False, default="active")
    current_wave = Column(Integer, nullable=False, default=0)
    wave_state = Column(JSONB, nullable=False, default=dict)
    book_config = Column(JSONB, nullable=False, default=dict)
    published_book_id = Column(Text, ForeignKey("books.id", ondelete="SET NULL"))
    total_tokens_used = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    deleted_at = Column(DateTime(timezone=True))

    account = relationship("Account")
    files = relationship("WritingFile", back_populates="session", cascade="all, delete-orphan")
    messages = relationship("WritingMessage", back_populates="session", cascade="all, delete-orphan")


class WritingFile(Base):
    __tablename__ = "writing_files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(Text, ForeignKey("writing_sessions.id", ondelete="CASCADE"), nullable=False)
    wave = Column(Integer, nullable=False)
    file_type = Column(Text, nullable=False)
    chapter_number = Column(Integer)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False, default="")
    word_count = Column(Integer, nullable=False, default=0)
    sort_order = Column(Integer, nullable=False, default=0)
    parent_file_id = Column(UUID(as_uuid=True), ForeignKey("writing_files.id", ondelete="SET NULL"))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))

    session = relationship("WritingSession", back_populates="files")


class WritingMessage(Base):
    __tablename__ = "writing_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(Text, ForeignKey("writing_sessions.id", ondelete="CASCADE"), nullable=False)
    wave = Column(Integer, nullable=False)
    role = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    files_generated = Column(JSONB, default=list)
    tokens_used = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))

    session = relationship("WritingSession", back_populates="messages")
