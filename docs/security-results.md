# Actual security results

First run: https://github.com/Prisha4gupta/ApplyTrail/actions/runs/38502731767, commit 28856e4. The frontend build/Trivy/push job passed. The backend build succeeded but Trivy returned failure on HIGH/CRITICAL findings; deployment was skipped. Full original reports are in evidence/trivy-{backend,frontend}-38502731767.json.

The backend report identifies Debian Bookworm OS packages, including CRITICAL CVE-2023-45853 in zlib1g and HIGH findings in util-linux-related libraries. Several records have no fixed version in that distribution; some Perl/pcre2 findings have a fixed Debian update. These are scanner-reported package findings, not proof that an attack was performed or that every vulnerable code path is reachable in this API.

Remediation: switch the backend to the verified Python 3.12.14 Alpine 3.24 base, apply available Alpine package updates at build, retain non-root operation and all existing dependency pins, then rebuild and rescan. This removes the old Debian package set rather than suppressing its findings. The new scan must pass the same HIGH/CRITICAL gate, including unfixed findings; the next real run passed for both images. No allowlist or ignore-unfixed flag was introduced.

The frontend report contains no HIGH/CRITICAL findings at that scan time. This does not mean there are no lower-severity issues or unknown vulnerabilities. Scanner databases change; rerun for every release.

## Remediation verified

Run https://github.com/Prisha4gupta/ApplyTrail/actions/runs/38586804223 at commit b547f76: both image build/scan/push jobs passed, with zero reported HIGH/CRITICAL findings in the retained JSON reports. PostgreSQL tests and the complete Compose runtime/persistence job also passed. Deployment failed at AWS credential configuration; no EKS rollout occurred. See evidence/ci-run-38586804223.json and the matching scan artifacts.
