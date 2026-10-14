#!/usr/bin/env python3
"""Real HTTP CRUD smoke test; always cleans its uniquely identified record."""
import json, os, sys, uuid
from urllib.request import Request, urlopen
base = sys.argv[1].rstrip('/')
identifier = None

def request(path, method='GET', data=None):
    body = json.dumps(data).encode() if data is not None else None
    with urlopen(Request(base+path,data=body,method=method,headers={'Content-Type':'application/json'}), timeout=15) as r:
        content = r.read()
        return json.loads(content) if content else None

try:
    with urlopen(base+'/',timeout=15) as response:
        assert b'<html' in response.read().lower(), 'Frontend is not serving HTML'
    version = request('/api/version')
    if os.getenv('EXPECTED_VERSION'):
        assert version['version']==os.environ['EXPECTED_VERSION'], 'Deployed version mismatch'
    body = {'company_name':'SMOKE-'+str(uuid.uuid4()),'role_title':'Synthetic verification','stage':'Applied'}
    app = request('/api/applications','POST',body)
    identifier = app['id']
    assert request(f'/api/applications/{identifier}')['company_name']==body['company_name']
    assert request(f'/api/applications/{identifier}','PUT',{**body,'stage':'Interview'})['stage']=='Interview'
    request(f'/api/applications/{identifier}/interviews','POST',{'scheduled_at':'2030-01-01T09:00:00Z','interview_type':'Video'})
    assert request('/api/dashboard')['interviews']>=1
    print('PASS: frontend, version, create, read, update, interview and dashboard')
finally:
    if identifier is not None:
        request(f'/api/applications/{identifier}','DELETE')
        assert not any(i['application_id']==identifier for i in request('/api/interviews'))
        print('PASS: smoke record and linked interview removed')
