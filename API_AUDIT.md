# API Audit Report

This report documents the security audit of the API endpoints in `backend/app/api/v1/`. The audit focused on identifying unprotected endpoints (those not requiring authentication).

## Summary

Most endpoints are correctly protected using `current_user: CurrentUser`. However, several critical vulnerabilities were found in `system.py`, `deployments.py`, `logs.py`, and `monitor.py` where authentication was either optional (`= None`) or missing (WebSockets).

## Detailed Analysis

| File | Status | Notes |
| :--- | :--- | :--- |
| `auth.py` | ✅ Protected | Public login endpoint is expected. Other endpoints protected. |
| `backups.py` | ✅ Protected | All endpoints require authentication. |
| `containers.py` | ✅ Protected | All endpoints require authentication. |
| `cron.py` | ✅ Protected | All endpoints require authentication. |
| `deployments.py` | ❌ **VULNERABLE** | Multiple endpoints (create, read, update, delete, etc.) have optional authentication (`CurrentUser = None`). WebSocket endpoint is protected. Webhook is public but verified. |
| `files.py` | ✅ Protected | All endpoints require authentication. |
| `firewall.py` | ✅ Protected | All endpoints require authentication. |
| `images.py` | ✅ Protected | All endpoints require authentication. |
| `logs.py` | ❌ **VULNERABLE** | `get_log_content` has optional authentication (`CurrentUser = None`). |
| `monitor.py` | ❌ **VULNERABLE** | WebSocket endpoint `/ws` is completely unprotected. HTTP endpoints are protected. |
| `mysql.py` | ✅ Protected | All endpoints require authentication. |
| `networks.py` | ✅ Protected | All endpoints require authentication. |
| `notifications.py` | ✅ Protected | All endpoints require authentication. |
| `postgres.py` | ✅ Protected | All endpoints require authentication. |
| `redis.py` | ✅ Protected | All endpoints require authentication. |
| `supervisor.py` | ✅ Protected | All endpoints require authentication. |
| `swarm.py` | ✅ Protected | All endpoints require authentication. |
| `system.py` | ❌ **VULNERABLE** | `list_directory` and `find_free_port` have optional authentication (`CurrentUser = None`). |
| `volumes.py` | ✅ Protected | All endpoints require authentication. |
| `waf.py` | ✅ Protected | All endpoints require authentication. |
| `websites.py` | ✅ Protected | All endpoints require authentication. |

## Identified Vulnerabilities & Fixes

### 1. `backend/app/api/v1/deployments.py`
**Issue:** `CurrentUser = None` used in `create_deployment`, `read_deployments`, `get_deployment`, `update_deployment`, `manual_trigger`, `clear_deployment_logs`, `delete_deployment`, `get_deployment_history`, `trigger_rollback`.
**Risk:** Unauthenticated users can view, modify, create, and delete deployments.
**Fix:** Remove `= None` to enforce authentication.

### 2. `backend/app/api/v1/system.py`
**Issue:** `CurrentUser = None` used in `list_directory` and `find_free_port`.
**Risk:** Unauthenticated users can list server directories and scan ports.
**Fix:** Remove `= None` to enforce authentication.

### 3. `backend/app/api/v1/logs.py`
**Issue:** `CurrentUser = None` used in `get_log_content`.
**Risk:** Unauthenticated users can read log files.
**Fix:** Remove `= None` to enforce authentication.

### 4. `backend/app/api/v1/monitor.py`
**Issue:** WebSocket endpoint `/ws` does not check for authentication.
**Risk:** Unauthenticated users can connect and receive real-time system stats.
**Fix:** Implement token-based authentication (JWT) for the WebSocket connection.
