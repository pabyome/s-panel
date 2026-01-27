## 2025-02-13 - Path Traversal via Prefix Match
**Vulnerability:** Path traversal allowed via `startswith` check on allowed roots.
**Learning:** `path.startswith("/tmp")` matches `/tmp-secret`.
**Prevention:** Ensure directory checks include trailing separator or use `os.path.commonpath`.
