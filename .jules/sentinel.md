# Security Learnings

## File Path Validation Symlink Traversal
- **Vulnerability**: Using `os.path.abspath` to validate paths against an allowed list can be bypassed using symbolic links that point outside the allowed roots.
- **Learning**: `abspath` only resolves `.` and `..` but preserves symlinks. This allows an attacker to create a symlink in an allowed directory pointing to a sensitive system directory.
- **Prevention**: Always use `os.path.realpath` to resolve symbolic links before checking if a path starts with an allowed root.
