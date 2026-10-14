from datetime import datetime, timezone, date
from sqlalchemy import String, Text, DateTime, ForeignKey, Date, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

def now():
    return datetime.now(timezone.utc)

class Application(Base):
    __tablename__ = 'applications'
    __table_args__ = (
        CheckConstraint("stage IN ('Saved','Applied','Screening','Interview','Offer','Rejected','Withdrawn')", name='application_stage'),
        CheckConstraint("employment_type IN ('Internship','Full-time','Part-time','Contract')", name='employment_type'),
        CheckConstraint("work_mode IN ('Remote','Hybrid','On-site')", name='work_mode'),
        CheckConstraint("length(trim(company_name)) > 0 AND length(trim(role_title)) > 0", name='required_names'),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    company_name: Mapped[str] = mapped_column(String(160), index=True)
    role_title: Mapped[str] = mapped_column(String(160), index=True)
    employment_type: Mapped[str] = mapped_column(String(20), index=True)
    work_mode: Mapped[str] = mapped_column(String(20))
    stage: Mapped[str] = mapped_column(String(20), index=True)
    location: Mapped[str | None] = mapped_column(String(200))
    job_url: Mapped[str | None] = mapped_column(String(2048))
    applied_date: Mapped[date | None] = mapped_column(Date)
    deadline: Mapped[date | None] = mapped_column(Date, index=True)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now, index=True)
    interviews: Mapped[list['Interview']] = relationship(back_populates='application', cascade='all, delete-orphan', passive_deletes=True)

class Interview(Base):
    __tablename__ = 'interviews'
    __table_args__ = (CheckConstraint("interview_type IN ('Phone','Video','On-site','Assessment')", name='interview_type'),)
    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey('applications.id', ondelete='CASCADE'), index=True)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    interview_type: Mapped[str] = mapped_column(String(20))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)
    application: Mapped[Application] = relationship(back_populates='interviews')
