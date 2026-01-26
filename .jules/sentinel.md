## 2024-05-23 - Path Traversal and Nginx Injection via Domain
**Vulnerability:** `WebsiteCreate` schema lacked validation for `domain`, allowing path traversal characters (`../`) and shell/config injection characters. This was passed directly to `NginxManager` which used it in file paths and config content.
**Learning:** Relying on generic string types in Pydantic schemas for sensitive fields (like file paths or system command arguments) is dangerous. Input validation must be explicit.
**Prevention:** Use `field_validator` to enforce strict patterns (regex) on all user inputs that touch the filesystem or shell commands.
