## 2024-05-22 - Partial Path Traversal in Allowed Roots
**Vulnerability:** The `list_directory` endpoint allowed access to sibling directories (e.g., `/tmp-secret`) because it used `clean_path.startswith(root)` to validate against `ALLOWED_ROOTS` like `/tmp`.
**Learning:** `startswith()` string matching is insufficient for path validation because it does not respect path separators.
**Prevention:** Always check for strict equality OR verify the path starts with `root + os.sep`.
