Notification System Design

Stage 1

Overview
This document defines the REST API contract for the Campus Notification Platform.
Users receive real-time updates for Placements, Events, and Results.

API Endpoints

1. Get All Notifications for a User
**GET** `/api/notifications`

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Response (200 OK):**
```json
{
  "notifications": [
    {
      "id": "uuid",
      "type": "Placement",
      "message": "CSX Corporation hiring",
      "isRead": false,
      "createdAt": "2026-04-22T17:51:18"
    }
  ]
}
```

2. Get a Single Notification
**GET** `/api/notifications/:id`

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "type": "Event",
  "message": "Tech fest tomorrow",
  "isRead": false,
  "createdAt": "2026-04-22T17:50:06"
}
```

---

3. Mark a Notification as Read
**PATCH** `/api/notifications/:id/read`

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "message": "Notification marked as read",
  "id": "uuid"
}
```

---

4. Mark All Notifications as Read
**PATCH** `/api/notifications/read-all`

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "message": "All notifications marked as read"
}
```

---

5. Get Unread Notification Count
**GET** `/api/notifications/unread-count`

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "unreadCount": 5
}
```

---

JSON Schemas

Notification Object
```json
{
  "id": "string (UUID)",
  "type": "enum: Placement | Result | Event",
  "message": "string",
  "isRead": "boolean",
  "createdAt": "string (ISO 8601 datetime)"
}
```

---

### Real-Time Notification Mechanism

For real-time notifications, we use **WebSockets** via **Socket.IO**.

**How it works:**
1. When a user logs in, their client connects to the WebSocket server
2. Each user joins a private room identified by their `studentID`
3. When a new notification is created (e.g. placement alert), the server emits it directly to that student's room
4. The frontend listens and instantly shows the notification without needing to refresh

**Why WebSockets over polling?**
- Polling means the frontend keeps asking the server "any new notifications?" every few seconds — this wastes resources
- WebSockets keep a persistent connection open — the server pushes data only when something actually happens
- Much faster, much lighter on the server

**Socket Event:**
```json
Event Name: "new_notification"
Payload: {
  "id": "uuid",
  "type": "Placement",
  "message": "CSX Corporation hiring",
  "createdAt": "2026-04-22T17:51:18"
}
```