#!/usr/bin/env python3
"""Exercise persistence and reversible Service failure in kind-applytrail only."""
import json
import subprocess
import time
import urllib.error
import urllib.request
import uuid

def kubectl(*args):
    return subprocess.check_output(['kubectl', *args], text=True)

assert kubectl('config', 'current-context').strip() == 'kind-applytrail', 'Local demo context required'
base = 'http://127.0.0.1:8080'

def request(path, method='GET', data=None):
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(base + path, data=body, method=method, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=5) as response:
        content = response.read()
        return json.loads(content) if content else None

def eventually(check, seconds=90):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        try:
            if check():
                return
        except (OSError, AssertionError):
            pass
        time.sleep(2)
    raise RuntimeError('Timed out waiting for expected state')

record = request('/api/applications', 'POST', {'company_name': 'RECOVERY-' + str(uuid.uuid4()), 'role_title': 'Disposable persistence check', 'stage': 'Applied'})
path = '/api/applications/' + str(record['id'])
original_selector = json.loads(kubectl('get', 'svc', 'backend', '-n', 'applytrail', '-o', 'json'))['spec']['selector']
try:
    kubectl('delete', 'pod', 'postgres-0', '-n', 'applytrail', '--wait=true')
    eventually(lambda: request(path)['company_name'] == record['company_name'])
    print('PASS: application record survived PostgreSQL pod recreation on its PVC', flush=True)
    try:
        kubectl('patch', 'svc', 'backend', '-n', 'applytrail', '--type=merge', '-p', json.dumps({'spec': {'selector': {'component': 'deliberate-demo-failure'}}}))
        def unavailable():
            try:
                request('/api/dashboard')
            except urllib.error.HTTPError as error:
                return error.code == 503
            return False
        eventually(unavailable, 30)
        print('PASS: deliberate selector mismatch produced HTTP 503', flush=True)
        print(kubectl('get', 'endpointslices', '-n', 'applytrail', '-l', 'kubernetes.io/service-name=backend'), flush=True)
    finally:
        kubectl('patch', 'svc', 'backend', '-n', 'applytrail', '--type=json', '-p', json.dumps([{'op': 'replace', 'path': '/spec/selector', 'value': original_selector}]))
    eventually(lambda: request(path)['company_name'] == record['company_name'])
    print('PASS: original selector restored; API and stored record recovered', flush=True)
finally:
    request(path, 'DELETE')
    print('Disposable recovery record removed', flush=True)
