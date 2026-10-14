#!/usr/bin/env python3
"""Verify persistence after application-container restart; clean synthetic record."""
import json, subprocess, time, uuid
from urllib.request import Request, urlopen
base='http://127.0.0.1:3000'
identifier=None

def request(path,method='GET',body=None):
    with urlopen(Request(base+path,method=method,data=json.dumps(body).encode() if body else None,headers={'Content-Type':'application/json'}),timeout=5) as r:
        data=r.read()
        return json.loads(data) if data else None

try:
    item=request('/api/applications','POST',{'company_name':'PERSISTENCE-'+str(uuid.uuid4()),'role_title':'Synthetic restart check'})
    identifier=item['id']
    subprocess.run(['docker','compose','restart','backend','frontend'],check=True)
    for attempt in range(30):
        try:
            persisted=request('/api/applications/'+str(identifier))
            assert persisted['company_name']==item['company_name']
            break
        except Exception:
            if attempt==29:raise
            time.sleep(2)
    print('PASS: application survives backend/frontend container restart')
finally:
    if identifier:
        request('/api/applications/'+str(identifier),'DELETE')
        print('PASS: persistence-check record removed')
