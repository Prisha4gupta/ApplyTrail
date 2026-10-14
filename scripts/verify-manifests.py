"""Validate rendered release invariants: python scripts/verify-manifests.py render.yaml."""
import sys, yaml
objects=list(yaml.safe_load_all(open(sys.argv[1])))
objects=[o for o in objects if o]
by_name={(o['kind'],o['metadata']['name']):o for o in objects}
front=by_name['Deployment','frontend'];back=by_name['Deployment','backend']
assert front['spec']['replicas']>=2
assert 'replicas' not in back['spec']
assert by_name['HorizontalPodAutoscaler','backend']['spec']['minReplicas']==2
for deployment in [front,back]:
    c=deployment['spec']['template']['spec']['containers'][0]
    assert c['resources']['requests']['cpu'] and c['readinessProbe'] and c['livenessProbe']
    assert c['securityContext']['runAsUser']>0
for name in ['frontend','backend']:
    assert by_name['Service',name]['spec']['type']=='ClusterIP'
paths=by_name['Ingress','applytrail']['spec']['rules'][0]['http']['paths']
assert {p['path']:p['backend']['service']['name'] for p in paths}=={'/':'frontend','/api':'backend'}
assert by_name['StatefulSet','postgres']['spec']['volumeClaimTemplates']
assert by_name['ServiceMonitor','applytrail']['metadata']['labels']['release']=='monitoring'
assert any(o['kind']=='Job' for o in objects)
print('PASS: replicas, HPA, resources, probes, non-root users, services, routing, PVC, migration and monitoring selectors')
