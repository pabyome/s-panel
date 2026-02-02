## 2025-05-15 - SQL Injection in PostgresManager
**Vulnerability:** Critical SQL injection in `PostgresManager` methods (`create_user`, `change_password`, `grant_access`, `manage_extension`) where user input (passwords, db names, etc.) was interpolated directly into SQL strings executed via `psql -c`.
**Learning:** Even when using `subprocess`, constructing SQL strings manually is dangerous. Shelling out to `psql` requires careful escaping of both shell arguments (handled by `subprocess` list) AND SQL literals/identifiers.
**Prevention:** Always use parameterized queries (e.g. `sqlalchemy`, `psycopg2`) when possible. If shelling out is unavoidable, strictly validate all inputs and use proper escaping (`'` -> `''` for literals, `"` -> `""` for identifiers).
