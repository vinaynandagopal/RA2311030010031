import requests
from logger import Log

ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiYXVkIjoiaHR0cDovLzIwLjI0NC41Ni4xNDQvZXZhbHVhdGlvbi1zZXJ2aWNlIiwiZW1haWwiOiJ2bjk1MTdAc3JtaXN0LmVkdS5pbiIsImV4cCI6MTc3NzcwNDM4MywiaWF0IjoxNzc3NzAzNDgzLCJpc3MiOiJBZmZvcmQgTWVkaWNhbCBUZWNobm9sb2dpZXMgUHJpdmF0ZSBMaW1pdGVkIiwianRpIjoiNmFmYjVlZDAtMjRhOC00Nzc2LTlmYTAtYzU5OTdhOWM5YmI2IiwibG9jYWxlIjoiZW4tSU4iLCJuYW1lIjoidmluYXlfbiIsInN1YiI6IjY2ZGY3ODYxLWIxNDYtNGNhZS04MzY3LWI0NWNhY2NiYjJjZSJ9LCJlbWFpbCI6InZuOTUxN0Bzcm1pc3QuZWR1LmluIiwibmFtZSI6InZpbmF5X24iLCJyb2xsTm8iOiJyYTIzMTEwMzAwMTAwMzEiLCJhY2Nlc3NDb2RlIjoiUWticHhIIiwiY2xpZW50SUQiOiI2NmRmNzg2MS1iMTQ2LTRjYWUtODM2Ny1iNDVjYWNjYmIyY2UiLCJjbGllbnRTZWNyZXQiOiJHbkhGZ1BxcVdwZVBRdlZWIn0.8EcJORJolTAX-Ge1n2-kgFhaSxb2Pp57s4mxD59fP1o"

BASE_URL = "http://20.207.122.201/evaluation-service"

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}


# ─────────────────────────────────────────
# Step 1: Fetch all depots
# ─────────────────────────────────────────
def get_depots():
    Log("backend", "info", "service", "Fetching depots from API")
    response = requests.get(f"{BASE_URL}/depots", headers=HEADERS)
    if response.status_code in (200, 201):
        data = response.json()
        Log("backend", "info", "service", f"Fetched {len(data['depots'])} depots")
        return data["depots"]
    else:
        Log("backend", "error", "service", f"Failed to fetch depots: {response.text}")
        return []


# ─────────────────────────────────────────
# Step 2: Fetch all vehicles
# ─────────────────────────────────────────
def get_vehicles():
    Log("backend", "info", "service", "Fetching vehicles from API")
    response = requests.get(f"{BASE_URL}/vehicles", headers=HEADERS)
    if response.status_code in (200, 201):
        data = response.json()
        Log("backend", "info", "service", f"Fetched {len(data['vehicles'])} vehicles")
        return data["vehicles"]
    else:
        Log("backend", "error", "service", f"Failed to fetch vehicles: {response.text}")
        return []


# ─────────────────────────────────────────
# Step 3: Knapsack algorithm
# Picks best vehicles within mechanic hours
# ─────────────────────────────────────────
def knapsack(vehicles, max_hours):
    n = len(vehicles)
    # Create a table of size (n+1) x (max_hours+1)
    dp = [[0] * (max_hours + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        duration = vehicles[i - 1]["Duration"]
        impact = vehicles[i - 1]["Impact"]
        for w in range(max_hours + 1):
            # Don't pick this vehicle
            dp[i][w] = dp[i - 1][w]
            # Pick this vehicle if it fits
            if duration <= w:
                dp[i][w] = max(dp[i][w], dp[i - 1][w - duration] + impact)

    # Trace back which vehicles were picked
    selected = []
    w = max_hours
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            selected.append(vehicles[i - 1])
            w -= vehicles[i - 1]["Duration"]

    return dp[n][max_hours], selected


# ─────────────────────────────────────────
# Step 4: Run for each depot
# ─────────────────────────────────────────
def main():
    depots = get_depots()
    vehicles = get_vehicles()

    if not depots or not vehicles:
        Log("backend", "fatal", "service", "Could not fetch data, aborting")
        return

    for depot in depots:
        depot_id = depot["ID"]
        max_hours = depot["MechanicHours"]

        Log("backend", "info", "service", f"Processing depot {depot_id} with {max_hours} mechanic hours")

        best_score, selected_vehicles = knapsack(vehicles, max_hours)

        total_hours = sum(v["Duration"] for v in selected_vehicles)

        print(f"\n{'='*50}")
        print(f"Depot ID     : {depot_id}")
        print(f"Max Hours    : {max_hours}")
        print(f"Total Hours Used : {total_hours}")
        print(f"Best Score   : {best_score}")
        print(f"Vehicles Selected ({len(selected_vehicles)}):")
        for v in selected_vehicles:
            print(f"  - TaskID: {v['TaskID']} | Duration: {v['Duration']}h | Impact: {v['Impact']}")

        Log("backend", "info", "service", f"Depot {depot_id} done. Score: {best_score}, Hours used: {total_hours}")


if __name__ == "__main__":
    main()