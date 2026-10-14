from datetime import datetime, timezone, timedelta
import pytest
from sqlalchemy.exc import OperationalError
from prometheus_client.parser import text_string_to_metric_families
from app.database import get_db
from app.main import app

BODY = {'company_name': 'Orbit Labs', 'role_title': 'Software Intern', 'stage': 'Applied'}

def create(client, **extra):
    response = client.post('/api/applications', json={**BODY, **extra})
    assert response.status_code == 201
    return response.json()

def test_create_and_read(client):
    item = create(client, applied_date='2020-01-01')
    assert item['applied_date'] == '2020-01-01'
    assert client.get(f"/api/applications/{item['id']}").json()['company_name'] == 'Orbit Labs'

def test_filters_pagination_sort(client):
    create(client, deadline='2030-01-01')
    create(client, company_name='Northstar', stage='Saved', employment_type='Full-time', deadline='2029-01-01')
    assert client.get('/api/applications?q=orbit').json()['total'] == 1
    assert client.get('/api/applications?stage=Saved&employment_type=Full-time').json()['items'][0]['company_name'] == 'Northstar'
    page = client.get('/api/applications?sort=deadline&page_size=1').json()
    assert page['total'] == 2 and page['items'][0]['company_name'] == 'Northstar'
    assert len(client.get('/api/applications?page=2&page_size=1').json()['items']) == 1
    assert client.get('/api/applications?q=%25').json()['total'] == 0

def test_update_stage(client):
    item = create(client)
    result = client.put(f"/api/applications/{item['id']}", json={**BODY, 'stage': 'Interview'})
    assert result.status_code == 200 and result.json()['stage'] == 'Interview'
    assert client.get('/api/dashboard').json()['interviews'] == 1

def test_delete_cascades_interviews(client):
    item = create(client)
    interview = client.post(f"/api/applications/{item['id']}/interviews", json={'scheduled_at':'2030-01-01T12:00:00+08:00','interview_type':'Video'})
    assert interview.status_code == 201
    assert client.delete(f"/api/applications/{item['id']}").status_code == 204
    assert client.get('/api/interviews').json() == []
    assert client.get(f"/api/applications/{item['id']}").status_code == 404

@pytest.mark.parametrize('path', ['/api/applications/999', '/api/interviews/999'])
def test_nonexistent_delete(client, path):
    assert client.delete(path).status_code == 404

@pytest.mark.parametrize('extra', [{'company_name':' '}, {'stage':'Unknown'}, {'job_url':'javascript:alert(1)'}, {'employment_type':'Volunteer'}, {'deadline':'nonsense'}])
def test_invalid_application(client, extra):
    assert client.post('/api/applications', json={**BODY, **extra}).status_code == 422

def test_interview_crud_and_timezone(client):
    item = create(client)
    body = {'scheduled_at':'2030-01-01T12:00:00+08:00','interview_type':'Video'}
    response = client.post(f"/api/applications/{item['id']}/interviews", json=body)
    assert response.status_code == 201
    interview = response.json()
    assert datetime.fromisoformat(interview['scheduled_at'].replace('Z','+00:00')).hour == 4
    assert client.get('/api/interviews').json()[0]['company_name'] == 'Orbit Labs'
    assert client.put(f"/api/interviews/{interview['id']}", json={**body, 'interview_type':'Phone'}).json()['interview_type'] == 'Phone'
    assert client.delete(f"/api/interviews/{interview['id']}").status_code == 204
    assert client.post('/api/applications/999/interviews', json=body).status_code == 404
    assert client.post(f"/api/applications/{item['id']}/interviews", json={**body,'scheduled_at':'2030-01-01T12:00:00'}).status_code == 422

def test_dashboard_precise_counts(client):
    for stage in ['Saved','Applied','Screening','Interview','Offer','Rejected','Withdrawn']:
        create(client, stage=stage, deadline='2030-01-01')
    result = client.get('/api/dashboard?today=2029-12-31').json()
    assert (result['total'],result['active'],result['interviews'],result['offers']) == (7,3,1,1)
    assert len(result['deadlines']) == 1 and result['deadlines'][0]['stage'] == 'Saved'
    assert client.get('/api/dashboard?today=2031-01-01').json()['deadlines'] == []

def test_readiness_and_liveness(client):
    assert client.get('/ready').status_code == 200
    class Broken:
        def execute(self, statement):
            raise OperationalError('SELECT 1', {}, Exception('unavailable'))
    app.dependency_overrides[get_db] = lambda: Broken()
    assert client.get('/ready').status_code == 503
    assert client.get('/health').status_code == 200

def test_prometheus_bounded_labels(client):
    client.get('/api/applications/987654')
    client.get('/random-secret-path')
    response = client.get('/metrics')
    assert response.status_code == 200
    families = list(text_string_to_metric_families(response.text))
    assert any(f.name == 'applytrail_http_requests' for f in families)
    assert '987654' not in response.text and 'random-secret-path' not in response.text
    assert 'route="/api/applications/{identifier}"' in response.text

def test_upcoming_only(client):
    item = create(client)
    for days in [-1, 1]:
        response = client.post(f"/api/applications/{item['id']}/interviews", json={'scheduled_at':(datetime.now(timezone.utc)+timedelta(days=days)).isoformat(),'interview_type':'Phone'})
        assert response.status_code == 201
    assert len(client.get('/api/interviews?upcoming=true').json()) == 1
    assert len(client.get('/api/dashboard').json()['upcoming_interviews']) == 1
