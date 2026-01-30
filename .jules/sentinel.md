## 2026-01-30 - Unvalidated Path Access in Log Viewer
**Vulnerability:** Arbitrary File Read and Truncation in `/api/v1/logs` endpoints allowed attackers to read or clear any file on the system.
**Learning:** Security checks were described in comments ("# Security: Validate path") but not implemented, leading to a false sense of security. Reliance on `subprocess.run(["tail", ...])` without path validation is dangerous.
**Prevention:** Always enforce strict, whitelist-based path validation using `os.path.realpath` to resolve symlinks before accessing files. Centralize validation logic to avoid missed checks.
