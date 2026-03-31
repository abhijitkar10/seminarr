# API Reference

Base URL: `http://localhost:8000`

Interactive docs: `http://localhost:8000/docs` (Swagger UI)

---

## Endpoints

### `GET /`
System info + endpoint listing.

### `POST /ingest`
Ingest authentication events (JSON array).

**Body:** `AuthEvent[]`

```json
[
  {
    "event_id": "abc-123",
    "user_id": "alice@corp.com",
    "timestamp": "2026-03-28T09:00:00",
    "resource": "crm",
    "action": "login",
    "success": true
  }
]
```

**Response:** `IngestResponse`
```json
{ "accepted": 1, "errors": [] }
```

### `POST /ingest/okta`
Ingest Okta System Log events. Normalizes to internal format.

**Body:** `dict[]` — raw Okta System Log JSON events.

### `POST /upload/csv`
Upload a CSV log file.

**Body:** `multipart/form-data` — field `file` (CSV)

**Response:** `IngestResponse`

### `POST /train`
Train the anomaly detection model on all stored features.

**Response:**
```json
{ "trained": true }
```

### `POST /score`
Score all stored features against the trained model.

**Response:**
```json
{ "scored": 150 }
```

### `GET /anomalies?limit=100`
List detected anomalies, most recent first.

**Response:** `Anomaly[]`
```json
[
  {
    "event_id": "abc-123",
    "user_id": "alice@corp.com",
    "timestamp": "2026-03-28T03:00:00",
    "score": 0.72,
    "risk": 2.1,
    "reasons": ["Off-hours access", "New device detected"],
    "feature_contributions": { "hour": 3.2, "new_device": 1.0, ... }
  }
]
```

### `GET /events/recent?limit=100`
List recent authentication events.

### `GET /users?limit=100`
List users with event counts.

### `GET /users/{user_id}/profile`
User baseline profile.

**Response:** `UserProfile`
```json
{
  "user_id": "alice@corp.com",
  "typical_hours": [9, 10, 11, 14, 15],
  "typical_locations": ["San Francisco, US"],
  "failure_rate": 0.02,
  "resource_frequency": { "crm": 45, "email": 30 }
}
```

---

## Schemas

### AuthEvent
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| event_id | string | yes | Unique event ID |
| user_id | string | yes | User identifier |
| timestamp | datetime | yes | ISO 8601 |
| resource | string | yes | Resource accessed |
| action | string | yes | login/access/logout/authorize |
| success | bool | yes | Whether action succeeded |
| ip_address | string | no | Source IP |
| latitude | float | no | Geo latitude |
| longitude | float | no | Geo longitude |
| location | string | no | City/Region |
| user_agent | string | no | Browser user agent |
| device_id | string | no | Device identifier |
| mfa_used | bool | no | MFA was used |
| failure_reason | string | no | Reason if failed |
| privilege_level | string | no | user/admin/svc |
