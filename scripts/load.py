#!/usr/bin/env python3
"""Bounded read-only load. Ctrl+C stops; maximum 300 seconds / 32 workers."""
import concurrent.futures, sys, time, urllib.request
url = sys.argv[1].rstrip('/') + '/api/applications?page_size=100'
seconds = min(300, max(1,int(sys.argv[2]) if len(sys.argv)>2 else 60))
workers = min(32,max(1,int(sys.argv[3]) if len(sys.argv)>3 else 8))
end = time.monotonic()+seconds

def worker():
    ok=failed=0
    while time.monotonic()<end:
        try:
            with urllib.request.urlopen(url,timeout=3) as r:
                r.read()
                ok+=1
        except Exception:
            failed+=1
    return ok,failed
try:
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        results=list(pool.map(lambda _:worker(),range(workers)))
    print({'successful':sum(r[0] for r in results),'failed':sum(r[1] for r in results),'seconds':seconds,'workers':workers})
except KeyboardInterrupt:
    end=0
    print('Stopping load; in-flight requests have a three-second timeout.')
