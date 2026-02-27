"""SQLAlchemy ORM models for lightpaper.org."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Boolean, Column, DateTime, FetchedValue, ForeignKey, Integer, Text, text
)
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR, UUID
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Account(Base):
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    firebase_uid = Column(Text, unique=True, nullable=False)
    handle = Column(Text, unique=True)
    display_name = Column(Text)
    email = Column(Text)
    bio = Column(Text)
    avatar_url = Column(Text)
    tier = Column(Text, nullable=False, default="free")
    verified_domain = Column(Text)
    verified_linkedin = Column(Boolean, default=False)
    orcid_id = Column(Text)
    gravity_level = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    deleted_at = Column(DateTime(timezone=True))

    api_keys = relationship("ApiKey", back_populates="account", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="account")


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
    search_vector = Column(TSVECTOR, FetchedValue())

    account = relationship("Account", back_populates="documents")
    versions = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan")


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


class AnonymousPublish(Base):
    __tablename__ = "anonymous_publishes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    ip_address = Column(Text, nullable=False)
    document_id = Column(Text, ForeignKey("documents.id", ondelete="SET NULL"))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))


class DomainVerification(Base):
    __tablename__ = "domain_verifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    domain = Column(Text, nullable=False)
    txt_token = Column(Text, nullable=False)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))


class LinkedInVerification(Base):
    __tablename__ = "linkedin_verifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    state_token = Column(Text, unique=True, nullable=False)
    verified = Column(Boolean, default=False)
    linkedin_profile_id = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
