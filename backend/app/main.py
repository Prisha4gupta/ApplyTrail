import os
from datetime import datetime, timezone, date
from time import perf_counter
from typing import Annotated, Literal
from fastapi import FastAPI, Depends, HTTPException, Query, Response, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select, func, or_, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from .database import get_db
from .models import Application, Interview
from .schemas import ApplicationInput, ApplicationOutput, ApplicationPage, InterviewInput, InterviewOutput, InterviewDetail, Dashboard, Stage, Employment

app = FastAPI(title='ApplyTrail', version='1.0.0')
DB = Annotated[Session, Depends(get_db)]
REQUESTS = Counter('applytrail_http_requests_total', 'HTTP requests', ['method', 'route', 'status'])
LATENCY = Histogram('applytrail_http_request_duration_seconds', 'Request duration', ['method', 'route'])

@app.middleware('http')
async def observe(request: Request, call_next):
    started = perf_counter()
    status = 500
    try:
        response = await call_next(request)
        status = response.status_code
        return response
    finally:
        route = getattr(request.scope.get('route'), 'path', 'unmatched')
        method = request.method if request.method in {'GET','POST','PUT','DELETE','PATCH','OPTIONS','HEAD'} else 'OTHER'
        REQUESTS.labels(method, route, str(status)).inc()
        LATENCY.labels(method, route).observe(perf_counter() - started)

@app.exception_handler(SQLAlchemyError)
async def db_error(request, exc):
    return JSONResponse(status_code=503, content={'detail': 'Database unavailable. Please retry.'})

@app.get('/health')
def health():
    return {'status': 'ok'}

@app.get('/ready')
def ready(db: DB):
    try:
        db.execute(text('SELECT 1'))
    except SQLAlchemyError:
        raise HTTPException(503, 'Database unavailable')
    return {'status': 'ready'}

@app.get('/metrics')
def metrics():
    return Response(generate_latest(), headers={'Content-Type': CONTENT_TYPE_LATEST})

@app.get('/api/version')
@app.get('/')
def version():
    return {'name': 'ApplyTrail', 'version': os.getenv('APP_VERSION', 'local')}

def get_or_404(db, model, identifier):
    item = db.get(model, identifier)
    if item is None:
        raise HTTPException(404, f'{model.__name__} not found')
    return item

def save(db, item):
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@app.get('/api/applications', response_model=ApplicationPage)
def applications(db: DB, q: str = Query('', max_length=160), stage: Stage | None = None, employment_type: Employment | None = None, sort: Literal['updated', 'deadline'] = 'updated', page: int = Query(1, ge=1), page_size: int = Query(12, ge=1, le=100)):
    statement = select(Application)
    if q.strip():
        escaped = q.strip().replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
        statement = statement.where(or_(Application.company_name.ilike(f'%{escaped}%', escape='\\'), Application.role_title.ilike(f'%{escaped}%', escape='\\')))
    if stage:
        statement = statement.where(Application.stage == stage)
    if employment_type:
        statement = statement.where(Application.employment_type == employment_type)
    total = db.scalar(select(func.count()).select_from(statement.subquery()))
    ordering = Application.updated_at.desc() if sort == 'updated' else Application.deadline.asc().nulls_last()
    items = db.scalars(statement.order_by(ordering, Application.id.desc()).offset((page-1)*page_size).limit(page_size)).all()
    return {'items': items, 'total': total, 'page': page, 'page_size': page_size}

@app.post('/api/applications', response_model=ApplicationOutput, status_code=201)
def create_application(body: ApplicationInput, db: DB):
    return save(db, Application(**body.model_dump()))

@app.get('/api/applications/{identifier}', response_model=ApplicationOutput)
def application(identifier: int, db: DB):
    return get_or_404(db, Application, identifier)

@app.put('/api/applications/{identifier}', response_model=ApplicationOutput)
def update_application(identifier: int, body: ApplicationInput, db: DB):
    item = get_or_404(db, Application, identifier)
    for key, value in body.model_dump().items():
        setattr(item, key, value)
    return save(db, item)

@app.delete('/api/applications/{identifier}', status_code=204)
def delete_application(identifier: int, db: DB):
    db.delete(get_or_404(db, Application, identifier))
    db.commit()
    return Response(status_code=204)

def detail(item):
    return {**InterviewOutput.model_validate(item).model_dump(), 'company_name': item.application.company_name, 'role_title': item.application.role_title}

@app.get('/api/interviews', response_model=list[InterviewDetail])
def interviews(db: DB, application_id: int | None = None, upcoming: bool = False):
    statement = select(Interview).options(joinedload(Interview.application)).order_by(Interview.scheduled_at, Interview.id)
    if application_id is not None:
        statement = statement.where(Interview.application_id == application_id)
    if upcoming:
        statement = statement.where(Interview.scheduled_at >= datetime.now(timezone.utc))
    return [detail(item) for item in db.scalars(statement).all()]

@app.post('/api/applications/{identifier}/interviews', response_model=InterviewOutput, status_code=201)
def create_interview(identifier: int, body: InterviewInput, db: DB):
    get_or_404(db, Application, identifier)
    return save(db, Interview(application_id=identifier, **body.model_dump()))

@app.put('/api/interviews/{identifier}', response_model=InterviewOutput)
def update_interview(identifier: int, body: InterviewInput, db: DB):
    item = get_or_404(db, Interview, identifier)
    for key, value in body.model_dump().items():
        setattr(item, key, value)
    return save(db, item)

@app.delete('/api/interviews/{identifier}', status_code=204)
def delete_interview(identifier: int, db: DB):
    db.delete(get_or_404(db, Interview, identifier))
    db.commit()
    return Response(status_code=204)

@app.get('/api/dashboard', response_model=Dashboard)
def dashboard(db: DB, today: date | None = None):
    # Client supplies its local calendar day; default is UTC for non-browser callers.
    today = today or datetime.now(timezone.utc).date()
    stages = dict(db.execute(select(Application.stage, func.count()).group_by(Application.stage)).all())
    upcoming = db.scalars(select(Interview).options(joinedload(Interview.application)).where(Interview.scheduled_at >= datetime.now(timezone.utc)).order_by(Interview.scheduled_at).limit(5)).all()
    deadlines = db.scalars(select(Application).where(Application.stage == 'Saved', Application.deadline >= today).order_by(Application.deadline, Application.id).limit(5)).all()
    return {'total': sum(stages.values()), 'active': sum(stages.get(s, 0) for s in ['Applied','Screening','Interview']), 'interviews': stages.get('Interview',0), 'offers': stages.get('Offer',0), 'stages': stages, 'upcoming_interviews': [detail(i) for i in upcoming], 'deadlines': deadlines}
