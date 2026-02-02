## 2024-10-26 - [WebSocket Broadcast Reliability]
**Learning:** A single unhandled exception in an async broadcast loop (e.g., `psutil` failure or network error) can terminate the entire background task, stopping updates for all clients.
**Action:** Always wrap the critical logic inside the `while True` loop with a broad `try...except` block to log the error and continue, ensuring the service remains resilient to transient failures.
