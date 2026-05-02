# Notification System Design

## Stage 1

### Overview
This document defines the REST API contract for the Campus Notification Platform.
Users receive real-time updates for Placements, Events, and Results.

---

### API Endpoints

#### 1. Get All Notifications for a User
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

---

#### 2. Get a Single Notification
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

#### 3. Mark a Notification as Read
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

#### 4. Mark All Notifications as Read
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

#### 5. Get Unread Notification Count
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

### JSON Schemas

#### Notification Object
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

## Stage 2

### Database Choice — PostgreSQL (Relational/SQL)

**Why PostgreSQL?**
- Notifications have a clear, structured format (id, type, message, isRead, createdAt) — relational DB fits perfectly
- We need to query by studentID, filter by isRead, sort by createdAt — SQL handles this naturally
- PostgreSQL supports indexing very well which helps with performance as data grows
- ACID compliance ensures no notification is lost or duplicated

---

### Database Schema

#### Students Table
```sql
CREATE TABLE students (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Notifications Table
```sql
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    type notification_type NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Enum for notification type
CREATE TYPE notification_type AS ENUM ('Placement', 'Result', 'Event');
```

---

### Queries Based on Stage 1 APIs

#### 1. Get all notifications for a user
```sql
SELECT id, type, message, is_read, created_at
FROM notifications
WHERE student_id = $1
ORDER BY created_at DESC;
```

#### 2. Get a single notification
```sql
SELECT id, type, message, is_read, created_at
FROM notifications
WHERE id = $1 AND student_id = $2;
```

#### 3. Mark a notification as read
```sql
UPDATE notifications
SET is_read = TRUE
WHERE id = $1 AND student_id = $2;
```

#### 4. Mark all notifications as read
```sql
UPDATE notifications
SET is_read = TRUE
WHERE student_id = $1;
```

#### 5. Get unread notification count
```sql
SELECT COUNT(*) as unread_count
FROM notifications
WHERE student_id = $1 AND is_read = FALSE;
```

---

### Problems as Data Grows

As the platform grows to 50,000 students with millions of notifications, these problems will arise:

1. **Slow queries** — Scanning the entire notifications table for one student becomes very slow without indexes
2. **High DB load** — Every page load triggers a query, putting constant pressure on the database
3. **Storage bloat** — Old notifications pile up and slow down the entire table
4. **Write bottlenecks** — When a placement alert goes to 50,000 students at once, 50,000 rows need to be inserted simultaneously

---

### Solutions

1. **Add indexes** on `student_id` and `created_at` so queries are fast even with millions of rows
```sql
CREATE INDEX idx_notifications_student_id ON notifications(student_id);
CREATE INDEX idx_notifications_created_at ON notifications(created_at DESC);
CREATE INDEX idx_notifications_unread ON notifications(student_id, is_read) WHERE is_read = FALSE;
```

2. **Caching** — Use Redis to cache each student's notifications so the DB is not hit on every page load

3. **Archiving** — Move notifications older than 6 months to an archive table to keep the main table small and fast

4. **Async writes** — Use a message queue (like RabbitMQ or Redis Queue) to handle bulk inserts when notifying all 50,000 students at once instead of writing all at once

## Stage 3

### Is the query accurate?

Yes, the query is logically correct as it fetches all unread notifications for a specific student ordered by newest first but at scale, the query has performance problems.

---

### Why is it slow?

1. **No index on studentID or isRead** — The database has to scan every single row in the notifications table to find matching rows. With 50,000 students and millions of notifications this is extremely slow
2. **SELECT \*** — Fetching all columns including ones the frontend may not need wastes memory and bandwidth
3. **No LIMIT** — If a student has 10,000 unread notifications, all of them are returned at once which overwhelms both the DB and the frontend

---

### What would you change?

**Improved query:**
```sql
SELECT id, type, message, created_at
FROM notifications
WHERE student_id = 1042 AND is_read = false
ORDER BY created_at DESC
LIMIT 20 OFFSET 0;
```

**Changes made:**
- Replace `SELECT *` with only needed columns
- Add `LIMIT` and `OFFSET` for pagination — only fetch 20 at a time
- Add indexes (see below) so the WHERE clause is fast

**Add these indexes:**
```sql
CREATE INDEX idx_notifications_student_id ON notifications(student_id);
CREATE INDEX idx_notifications_unread ON notifications(student_id, is_read) WHERE is_read = FALSE;
CREATE INDEX idx_notifications_created_at ON notifications(created_at DESC);
```

---

### Is adding indexes on every column a good idea?

**No, this is bad advice.** Here is why:

- Every index takes up extra storage space on disk
- Every time a new notification is inserted or updated, ALL indexes on that table must also be updated — this makes writes significantly slower
- Most columns are never used in WHERE clauses so indexing them gives zero benefit but adds cost
- The right approach is to only index columns that are frequently used in WHERE, ORDER BY, or JOIN conditions

**Good columns to index:** `student_id`, `is_read`, `created_at`, `type`
**Bad columns to index:** `message`, `id` (already primary key)

---

### Query — Students who got a Placement notification in the last 7 days

```sql
SELECT DISTINCT student_id
FROM notifications
WHERE type = 'Placement'
AND created_at >= NOW() - INTERVAL '7 days';
```

If you want student details too:
```sql
SELECT DISTINCT s.id, s.name, s.email
FROM students s
JOIN notifications n ON s.id = n.student_id
WHERE n.type = 'Placement'
AND n.created_at >= NOW() - INTERVAL '7 days';
```