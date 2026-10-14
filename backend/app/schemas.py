from datetime import date, datetime, timezone
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, AwareDatetime, HttpUrl, field_validator

Stage = Literal['Saved', 'Applied', 'Screening', 'Interview', 'Offer', 'Rejected', 'Withdrawn']
Employment = Literal['Internship', 'Full-time', 'Part-time', 'Contract']

class ApplicationInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')
    company_name: str = Field(min_length=1, max_length=160)
    role_title: str = Field(min_length=1, max_length=160)
    employment_type: Employment = 'Internship'
    work_mode: Literal['Remote', 'Hybrid', 'On-site'] = 'Hybrid'
    stage: Stage = 'Saved'
    location: str | None = Field(default=None, max_length=200)
    job_url: str | None = Field(default=None, max_length=2048)
    applied_date: date | None = None
    deadline: date | None = None
    notes: str | None = Field(default=None, max_length=10000)

    @field_validator('job_url')
    @classmethod
    def valid_url(cls, value):
        if value is not None:
            HttpUrl(value)
        return value

class ApplicationOutput(ApplicationInput):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime

class ApplicationPage(BaseModel):
    items: list[ApplicationOutput]
    total: int
    page: int
    page_size: int

class InterviewInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    scheduled_at: AwareDatetime
    interview_type: Literal['Phone', 'Video', 'On-site', 'Assessment']
    notes: str | None = Field(default=None, max_length=10000)

    @field_validator('scheduled_at')
    @classmethod
    def utc(cls, value):
        return value.astimezone(timezone.utc)

class InterviewOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    application_id: int
    scheduled_at: datetime
    interview_type: str
    notes: str | None
    created_at: datetime
    updated_at: datetime

    @field_validator('scheduled_at', 'created_at', 'updated_at')
    @classmethod
    def ensure_timezone(cls, value):
        return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value

class InterviewDetail(InterviewOutput):
    company_name: str
    role_title: str

class Dashboard(BaseModel):
    total: int
    active: int
    interviews: int
    offers: int
    stages: dict[str, int]
    upcoming_interviews: list[InterviewDetail]
    deadlines: list[ApplicationOutput]
