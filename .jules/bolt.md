## 2024-05-23 - psutil concurrency and Set iteration
**Learning:** `psutil.cpu_percent(interval=None)` maintains global/shared state regarding the "last call" time. Concurrent calls from different threads or tasks will race and reset this timer, causing subsequent calls to return inaccurate values (often near 0.0 or 100.0) because the time delta becomes tiny.
**Action:** When using `psutil.cpu_percent` in a concurrent environment (like WebSockets), use a single background task to query the stats and broadcast the result, rather than having each client poll independently.

**Learning:** Iterating over a `set` of active WebSocket connections while `await`ing `send_json` inside the loop is a bug. `await` yields control, allowing other tasks to connect/disconnect and modify the set, raising `RuntimeError: Set changed size during iteration`.
**Action:** Always iterate over a copy of the set (e.g., `list(active_connections)`) when performing async operations inside the loop.
