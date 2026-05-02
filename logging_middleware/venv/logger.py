import requests

# ✅ Paste your actual token here (the one you got from Postman)
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiYXVkIjoiaHR0cDovLzIwLjI0NC41Ni4xNDQvZXZhbHVhdGlvbi1zZXJ2aWNlIiwiZW1haWwiOiJ2bjk1MTdAc3JtaXN0LmVkdS5pbiIsImV4cCI6MTc3NzY5OTA4NywiaWF0IjoxNzc3Njk4MTg3LCJpc3MiOiJBZmZvcmQgTWVkaWNhbCBUZWNobm9sb2dpZXMgUHJpdmF0ZSBMaW1pdGVkIiwianRpIjoiMTk2NjM1YzEtMWQxNi00NzY3LWEyMGEtMzI1NTZlOTBmYjAyIiwibG9jYWxlIjoiZW4tSU4iLCJuYW1lIjoidmluYXlfbiIsInN1YiI6IjY2ZGY3ODYxLWIxNDYtNGNhZS04MzY3LWI0NWNhY2NiYjJjZSJ9LCJlbWFpbCI6InZuOTUxN0Bzcm1pc3QuZWR1LmluIiwibmFtZSI6InZpbmF5X24iLCJyb2xsTm8iOiJyYTIzMTEwMzAwMTAwMzEiLCJhY2Nlc3NDb2RlIjoiUWticHhIIiwiY2xpZW50SUQiOiI2NmRmNzg2MS1iMTQ2LTRjYWUtODM2Ny1iNDVjYWNjYmIyY2UiLCJjbGllbnRTZWNyZXQiOiJHbkhGZ1BxcVdwZVBRdlZWIn0.S4NwbqisLlDtlsPziKkvAvfFyiIU2WjHmAwNxgojbqc"

LOG_API_URL = "http://20.207.122.201/evaluation-service/logs"

# Valid values — the server will reject anything outside these
VALID_STACKS = {"backend", "frontend"}
VALID_LEVELS = {"debug", "info", "warn", "error", "fatal"}
VALID_PACKAGES_BACKEND = {
    "cache", "controller", "cron_job", "db", "domain",
    "handler", "repository", "route", "service"
}
VALID_PACKAGES_FRONTEND = {"api", "component", "hook", "page", "state", "style"}
VALID_PACKAGES_BOTH = {"auth", "config", "middleware", "utils"}


def Log(stack, level, package, message):
    """
    Sends a log entry to the Affordmed test server.

    Parameters:
        stack   : "backend" or "frontend"
        level   : "debug", "info", "warn", "error", or "fatal"
        package : the part of your code that is logging (e.g. "db", "handler")
        message : what happened (e.g. "Database connection failed")
    """

    # --- Basic validation ---
    if stack not in VALID_STACKS:
        print(f"[LOG ERROR] Invalid stack: '{stack}'. Must be one of {VALID_STACKS}")
        return None

    if level not in VALID_LEVELS:
        print(f"[LOG ERROR] Invalid level: '{level}'. Must be one of {VALID_LEVELS}")
        return None

    # Check package is valid for the given stack
    if stack == "backend":
        allowed_packages = VALID_PACKAGES_BACKEND | VALID_PACKAGES_BOTH
    else:
        allowed_packages = VALID_PACKAGES_FRONTEND | VALID_PACKAGES_BOTH

    if package not in allowed_packages:
        print(f"[LOG ERROR] Invalid package: '{package}' for stack '{stack}'. Allowed: {allowed_packages}")
        return None

    # --- Build the request ---
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    body = {
        "stack": stack,
        "level": level,
        "package": package,
        "message": message
    }

    # --- Send the request ---
    try:
        response = requests.post(LOG_API_URL, json=body, headers=headers)

        if response.status_code == 200:
            data = response.json()
            print(f"[LOG SUCCESS] logID: {data.get('logID')} | {stack} | {level} | {package} | {message}")
            return data
        else:
            print(f"[LOG FAILED] Status: {response.status_code} | Response: {response.text}")
            return None

    except Exception as e:
        print(f"[LOG EXCEPTION] Could not send log: {e}")
        return None


# ✅ Test it — run this file directly to verify it works
if __name__ == "__main__":
    Log("backend", "info", "db", "Database connection established successfully")
    Log("backend", "error", "handler", "Received string, expected bool")
    Log("backend", "fatal", "db", "Critical database connection failure")