## 2024-05-23 - [Resilient Broadcast Loops]
**Learning:** Background tasks (like WebSocket broadcasters) running infinite loops must handle exceptions *inside* the loop. If a `try/except` wraps the entire loop, a single transient error kills the task forever, leaving clients connected but receiving no data.
**Action:** Always wrap the body of the `while True` loop in a `try/except` block to catch, log, and continue.
