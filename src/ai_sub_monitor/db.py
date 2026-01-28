from __future__ import annotations

import uuid
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, Generator, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    DECIMAL,
    ForeignKey,
    String,
    create_engine,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship

from .config import default_db_path, ensure_data_dirs


class Base(DeclarativeBase):
  pass


class Company(Base):
  __tablename__ = "companies"

  id: Mapped[str] = mapped_column(String, primary_key=True)
  name: Mapped[str] = mapped_column(String, nullable=False)
  metadata_json: Mapped[Dict[str, Any] | None] = mapped_column("metadata", JSON, nullable=True)

  pricing_snapshots: Mapped[list["PricingSnapshot"]] = relationship(back_populates="company")
  rate_limit_changes: Mapped[list["RateLimitChange"]] = relationship(back_populates="company")
  community_signals: Mapped[list["CommunitySignal"]] = relationship(back_populates="company")
  financial_events: Mapped[list["FinancialEvent"]] = relationship(back_populates="company")


class PricingSnapshot(Base):
    __tablename__ = "pricing_snapshots"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id: Mapped[str] = mapped_column(String, ForeignKey("companies.id"), index=True)
    url: Mapped[str | None] = mapped_column(String, nullable=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    content_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    tier_name: Mapped[str] = mapped_column(String)
    price_monthly: Mapped[float | None] = mapped_column(DECIMAL(10, 2), nullable=True)
    price_annual: Mapped[float | None] = mapped_column(DECIMAL(10, 2), nullable=True)
    features: Mapped[Dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    rate_limits_stated: Mapped[Dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    raw_html: Mapped[str | None] = mapped_column(String, nullable=True)
    is_change: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    company: Mapped[Company] = relationship(back_populates="pricing_snapshots")


class DocumentationSnapshot(Base):
    __tablename__ = "documentation_snapshots"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id: Mapped[str] = mapped_column(String, ForeignKey("companies.id"), index=True)
    url: Mapped[str | None] = mapped_column(String, nullable=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    content_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    raw_html: Mapped[str | None] = mapped_column(String, nullable=True)
    is_change: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    company: Mapped[Company] = relationship()


class RateLimitChange(Base):
  __tablename__ = "rate_limit_changes"

  id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
  company_id: Mapped[str] = mapped_column(String, ForeignKey("companies.id"), index=True)
  detected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
  source: Mapped[str] = mapped_column(String)
  tier_affected: Mapped[str | None] = mapped_column(String, nullable=True)
  previous_limit: Mapped[Dict[str, Any] | None] = mapped_column(JSON, nullable=True)
  new_limit: Mapped[Dict[str, Any] | None] = mapped_column(JSON, nullable=True)
  change_description: Mapped[str | None] = mapped_column(String, nullable=True)
  evidence_urls: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

  company: Mapped[Company] = relationship(back_populates="rate_limit_changes")


class CommunitySignal(Base):
  __tablename__ = "community_signals"

  id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
  company_id: Mapped[str] = mapped_column(String, ForeignKey("companies.id"), index=True)
  source: Mapped[str] = mapped_column(String)  # reddit | github | twitter | discord
  source_id: Mapped[str] = mapped_column(String)
  captured_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
  content: Mapped[str] = mapped_column(String)
  url: Mapped[str | None] = mapped_column(String, nullable=True)
  sentiment: Mapped[float | None] = mapped_column(DECIMAL(4, 3), nullable=True)
  keywords_matched: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
  score: Mapped[int | None] = mapped_column(nullable=True)
  comment_count: Mapped[int | None] = mapped_column(nullable=True)

  company: Mapped[Company] = relationship(back_populates="community_signals")


class FinancialEvent(Base):
  __tablename__ = "financial_events"

  id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
  company_id: Mapped[str] = mapped_column(String, ForeignKey("companies.id"), index=True)
  event_date: Mapped[date] = mapped_column(Date, index=True)
  event_type: Mapped[str] = mapped_column(String)
  amount: Mapped[float | None] = mapped_column(DECIMAL(14, 2), nullable=True)
  valuation: Mapped[float | None] = mapped_column(DECIMAL(14, 2), nullable=True)
  source_url: Mapped[str | None] = mapped_column(String, nullable=True)
  notes: Mapped[str | None] = mapped_column(String, nullable=True)
  raw_data: Mapped[Dict[str, Any] | None] = mapped_column(JSON, nullable=True)

  company: Mapped[Company] = relationship(back_populates="financial_events")


class WeeklyReport(Base):
  __tablename__ = "weekly_reports"

  id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
  week_start: Mapped[date] = mapped_column(Date, index=True)
  week_end: Mapped[date] = mapped_column(Date, index=True)
  generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
  summary: Mapped[str | None] = mapped_column(String, nullable=True)
  rate_limit_changes: Mapped[int | None] = mapped_column(nullable=True)
  pricing_changes: Mapped[int | None] = mapped_column(nullable=True)
  community_signal_volume: Mapped[Dict[str, Any] | None] = mapped_column(JSON, nullable=True)
  sentiment_trend: Mapped[float | None] = mapped_column(DECIMAL(5, 3), nullable=True)
  key_events: Mapped[Dict[str, Any] | None] = mapped_column(JSON, nullable=True)


def get_engine(db_path: Path | None = None):
    db_path = db_path or default_db_path()
    ensure_data_dirs()
    url = f"sqlite:///{db_path}"
    return create_engine(url, echo=False, future=True)


def init_db(db_path: Path | None = None):
    engine = get_engine(db_path)
    Base.metadata.create_all(engine)
    _apply_migrations(engine)
    return engine


def _column_exists(engine, table: str, column: str) -> bool:
    with engine.connect() as conn:
        res = conn.execute(text(f"PRAGMA table_info('{table}')"))
        return any(row[1] == column for row in res.fetchall())


def _add_column(engine, table: str, column_def: str):
    with engine.connect() as conn:
        conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column_def}"))
        conn.commit()


def _apply_migrations(engine):
    # Add new columns to pricing_snapshots if missing
    if _column_exists(engine, "pricing_snapshots", "url") is False:
        _add_column(engine, "pricing_snapshots", "url TEXT")
    if _column_exists(engine, "pricing_snapshots", "content_hash") is False:
        _add_column(engine, "pricing_snapshots", "content_hash TEXT")
    if _column_exists(engine, "pricing_snapshots", "is_change") is False:
        _add_column(engine, "pricing_snapshots", "is_change BOOLEAN DEFAULT 0 NOT NULL")


@contextmanager
def session_scope(db_path: Path | None = None) -> Generator[Session, None, None]:
  engine = get_engine(db_path)
  session = Session(engine)
  try:
    yield session
    session.commit()
  except Exception:
    session.rollback()
    raise
  finally:
    session.close()
