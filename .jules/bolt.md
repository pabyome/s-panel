## 2024-05-22 - [WebSocket Polling Anti-Pattern]
**Learning:** Found critical scalability issue where WebSocket endpoints were spawning individual polling threads for each client (O(N) resource usage).
**Action:** Always implement a `ConnectionManager` with a single broadcast loop for shared real-time data to ensure O(1) resource usage regardless of client count.

## 2024-05-22 - [Broken Test Suite]
**Learning:** The existing test suite has multiple failures (Cron, Email, Firewall) unrelated to current work.
**Action:** When verifying changes, rely on new targeted tests and ensure no *new* regressions, rather than expecting a clean full suite run.
