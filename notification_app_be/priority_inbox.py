import requests
import heapq
import sys
sys.path.append(r'C:\Users\vinay\OneDrive\Desktop\RA2311030010031\logging_middleware')
from logger import Log

ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiYXVkIjoiaHR0cDovLzIwLjI0NC41Ni4xNDQvZXZhbHVhdGlvbi1zZXJ2aWNlIiwiZW1haWwiOiJ2bjk1MTdAc3JtaXN0LmVkdS5pbiIsImV4cCI6MTc3NzcwNDM4MywiaWF0IjoxNzc3NzAzNDgzLCJpc3MiOiJBZmZvcmQgTWVkaWNhbCBUZWNobm9sb2dpZXMgUHJpdmF0ZSBMaW1pdGVkIiwianRpIjoiNmFmYjVlZDAtMjRhOC00Nzc2LTlmYTAtYzU5OTdhOWM5YmI2IiwibG9jYWxlIjoiZW4tSU4iLCJuYW1lIjoidmluYXlfbiIsInN1YiI6IjY2ZGY3ODYxLWIxNDYtNGNhZS04MzY3LWI0NWNhY2NiYjJjZSJ9LCJlbWFpbCI6InZuOTUxN0Bzcm1pc3QuZWR1LmluIiwibmFtZSI6InZpbmF5X24iLCJyb2xsTm8iOiJyYTIzMTEwMzAwMTAwMzEiLCJhY2Nlc3NDb2RlIjoiUWticHhIIiwiY2xpZW50SUQiOiI2NmRmNzg2MS1iMTQ2LTRjYWUtODM2Ny1iNDVjYWNjYmIyY2UiLCJjbGllbnRTZWNyZXQiOiJHbkhGZ1BxcVdwZVBRdlZWIn0.8EcJORJolTAX-Ge1n2-kgFhaSxb2Pp57s4mxD59fP1o"

BASE_URL = "http://20.207.122.201/evaluation-service"

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

#lower the number, higher the priority
PRIORITY = {
    "Placement": 1,
    "Result": 2,
    "Event": 3
}


#fetch the notifications 
def get_notifications():
    Log("backend", "info", "service", "Fetching notifications from API")
    response = requests.get(f"{BASE_URL}/notifications", headers=HEADERS)
    if response.status_code in (200, 201):
        data = response.json()
        Log("backend", "info", "service", f"Fetched notifications successfully")
        return data["notifications"]
    else:
        Log("backend", "error", "service", f"Failed to fetch notifications: {response.text}")
        return []

def get_top_n_notifications(notifications, n):
    """
    Priority rules:
    1. PThe order of priority is placement-result-event
    2. Within same type, newer timestamp wins
    
    We use a heap where each entry is:
    (priority_number, negated_timestamp, notification)
    Smaller value = comes out first from heap
    """

    heap = []

    for notif in notifications:
        priority = PRIORITY.get(notif["Type"], 99)
        # Negate timestamp so newer = smaller number = higher priority
        timestamp = -int(notif["Timestamp"].replace("-", "").replace(":", "").replace(" ", ""))

        # Push into heap
        heapq.heappush(heap, (priority, timestamp, notif))

    top_n = []
    for _ in range(min(n, len(heap))):
        _, _, notif = heapq.heappop(heap)
        top_n.append(notif)

    return top_n


def display_notifications(notifications, n):
    print(f"\n{'='*60}")
    print(f"  TOP {n} PRIORITY NOTIFICATIONS")
    print(f"{'='*60}")

    for i, notif in enumerate(notifications, 1):
        print(f"\n#{i}")
        print(f"  Type      : {notif['Type']}")
        print(f"  Message   : {notif['Message']}")
        print(f"  Timestamp : {notif['Timestamp']}")
        print(f"  ID        : {notif['ID']}")

    print(f"\n{'='*60}")


def main():
    # Change this number to get top 10,15,etc
    N = 10

    notifications = get_notifications()

    if not notifications:
        Log("backend", "fatal", "service", "No notifications found, aborting")
        return

    Log("backend", "info", "service", "Finding top N priority notifications")

    top_n = get_top_n_notifications(notifications, N)

    display_notifications(top_n, N)

    Log("backend", "info", "service", "Top N notifications displayed")


if __name__ == "__main__":
    main()