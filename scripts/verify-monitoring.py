#!/usr/bin/env python3
"""Verify live Prometheus targets and every committed Grafana panel query.

Requires the intended KUBECONFIG. Does not print credentials or create test data.
"""
import base64
import json
import subprocess
import time
import urllib.parse
import urllib.request
from pathlib import Path

forward = subprocess.Popen(
    ['kubectl', '-n', 'monitoring', 'port-forward',
     'svc/monitoring-kube-prometheus-prometheus', '19090:9090'],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
)
grafana_forward = subprocess.Popen(
    ['kubectl', '-n', 'monitoring', 'port-forward', 'svc/monitoring-grafana', '13001:80'],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
)

def get(path):
    with urllib.request.urlopen('http://127.0.0.1:19090' + path, timeout=5) as response:
        return json.load(response)

try:
    deadline = time.monotonic() + 120
    last = 'Waiting for Prometheus'
    while time.monotonic() < deadline:
        try:
            targets = get('/api/v1/targets')['data']['activeTargets']
            app = [t for t in targets if t['labels'].get('namespace') == 'applytrail'
                   and t['labels'].get('service') == 'backend']
            assert len(app) >= 2 and all(t['health'] == 'up' for t in app), 'Backend targets are not all UP'
            results = {}
            dashboard = json.loads(Path('monitoring/dashboard.json').read_text())
            for panel in dashboard['panels']:
                query = panel['targets'][0]['expr']
                response = get('/api/v1/query?' + urllib.parse.urlencode({'query': query}))
                samples = response['data']['result']
                assert samples, f"No samples for {panel['title']}"
                values = [float(s['value'][1]) for s in samples]
                assert all(v == v and abs(v) != float('inf') for v in values), f"Invalid samples for {panel['title']}"
                results[panel['title']] = values
            secret = json.loads(subprocess.check_output(['kubectl', '-n', 'monitoring', 'get', 'secret', 'grafana-admin', '-o', 'json'], text=True))['data']
            user = base64.b64decode(secret['admin-user']).decode()
            password = base64.b64decode(secret['admin-password']).decode()
            auth = base64.b64encode(f'{user}:{password}'.encode()).decode()
            req = urllib.request.Request('http://127.0.0.1:13001/api/dashboards/uid/applytrail', headers={'Authorization': 'Basic ' + auth})
            with urllib.request.urlopen(req, timeout=10) as response:
                live_dashboard = json.load(response)['dashboard']
            assert live_dashboard['title'] == dashboard['title'], 'Grafana dashboard not provisioned'
            assert len(live_dashboard['panels']) == len(dashboard['panels']), 'Grafana panel count mismatch'
            print(json.dumps({'backend_targets_up': len(app), 'grafana_dashboard': live_dashboard['title'], 'panel_values': results}, indent=2))
            break
        except (AssertionError, OSError, KeyError) as error:
            last = str(error)
            time.sleep(5)
    else:
        raise SystemExit(last)
finally:
    forward.terminate()
    forward.wait(timeout=10)
    grafana_forward.terminate()
    grafana_forward.wait(timeout=10)
