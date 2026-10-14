#!/usr/bin/env bash
set -euo pipefail
: "${IMAGE_REPOSITORY:?Set GHCR repository prefix}"
: "${IMAGE_TAG:?Set full commit SHA}"
# Serialize through GitHub concurrency. Bootstrap namespace, secrets and controllers first.
helm upgrade --install applytrail helm/applytrail -n applytrail \
  --set-string image.repository="$IMAGE_REPOSITORY" \
  --set-string image.tag="$IMAGE_TAG" \
  --set monitoring.enabled=true --wait --atomic --timeout 10m
kubectl rollout status deployment/backend -n applytrail --timeout=180s
kubectl rollout status deployment/frontend -n applytrail --timeout=180s
kubectl get deployments -n applytrail -o wide
# The Ingress address is populated by Traefik publishedService.
address=$(kubectl get ingress applytrail -n applytrail -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
if [ -z "$address" ]; then
  address=$(kubectl get ingress applytrail -n applytrail -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
fi
: "${address:?Ingress address not yet ready}"
for attempt in $(seq 1 20); do
  if EXPECTED_VERSION="$IMAGE_TAG" python3 scripts/smoke.py "http://$address"; then exit 0; fi
  sleep 5
done
exit 1
