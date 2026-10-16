"""Explicit, idempotent fictional seed: python -m app.seed."""
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from .database import SessionLocal
from .models import Application, Interview

DATA = [
    ('Orbit Labs','Frontend Engineering Intern','Interview','Remote'),
    ('Northstar Studio','Product Design Intern','Applied','Hybrid'),
    ('Fern & Co.','Software Engineer','Offer','Hybrid'),
    ('Cloudberry','DevOps Intern','Screening','Remote'),
    ('Lumen Systems','Backend Engineering Intern','Saved','On-site'),
    ('Paperplane','Full Stack Intern','Applied','Remote'),
    ('Juniper Digital','Platform Engineer','Saved','Hybrid'),
    ('Tideworks','Data Analyst Intern','Rejected','Hybrid'),
]

def seed():
    now = datetime.now(timezone.utc)
    with SessionLocal.begin() as db:
        for index, (company,role,stage,mode) in enumerate(DATA):
            existing = db.scalar(select(Application).where(Application.company_name == company, Application.role_title == role))
            if existing:
                continue
            item = Application(company_name=company, role_title=role, employment_type='Internship' if 'Intern' in role else 'Full-time', work_mode=mode, stage=stage, location='Fictional demo company', applied_date=(now-timedelta(days=5+index)).date() if stage!='Saved' else None, deadline=(now+timedelta(days=index+2)).date() if stage=='Saved' else None, job_url='https://example.com/careers', notes='Fictional sample application for exploring ApplyTrail.')
            db.add(item)
            db.flush()
            if stage=='Interview':
                db.add(Interview(application_id=item.id, scheduled_at=now+timedelta(days=2), interview_type='Video', notes='Discuss a fictional portfolio project.'))
    print('Fictional demonstration data loaded; existing records preserved.')

if __name__ == '__main__':
    seed()
