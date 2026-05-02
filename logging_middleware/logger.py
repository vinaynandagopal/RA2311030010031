import requests

ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiYXVkIjoiaHR0cDovLzIwLjI0NC41Ni4xNDQvZXZhbHVhdGlvbi1zZXJ2aWNlIiwiZW1haWwiOiJ2bjk1MTdAc3JtaXN0LmVkdS5pbiIsImV4cCI6MTc3NzcwNDM4MywiaWF0IjoxNzc3NzAzNDgzLCJpc3MiOiJBZmZvcmQgTWVkaWNhbCBUZWNobm9sb2dpZXMgUHJpdmF0ZSBMaW1pdGVkIiwianRpIjoiNmFmYjVlZDAtMjRhOC00Nzc2LTlmYTAtYzU5OTdhOWM5YmI2IiwibG9jYWxlIjoiZW4tSU4iLCJuYW1lIjoidmluYXlfbiIsInN1YiI6IjY2ZGY3ODYxLWIxNDYtNGNhZS04MzY3LWI0NWNhY2NiYjJjZSJ9LCJlbWFpbCI6InZuOTUxN0Bzcm1pc3QuZWR1LmluIiwibmFtZSI6InZpbmF5X24iLCJyb2xsTm8iOiJyYTIzMTEwMzAwMTAwMzEiLCJhY2Nlc3NDb2RlIjoiUWticHhIIiwiY2xpZW50SUQiOiI2NmRmNzg2MS1iMTQ2LTRjYWUtODM2Ny1iNDVjYWNjYmIyY2UiLCJjbGllbnRTZWNyZXQiOiJHbkhGZ1BxcVdwZVBRdlZWIn0.8EcJORJolTAX-Ge1n2-kgFhaSxb2Pp57s4mxD59fP1o"

LOG_API_URL = "http://20.207.122.201/evaluation-service/logs"

VALID_STACKS = {"backend", "frontend"}
VALID_LEVELS = {"debug", "info", "warn", "error", "fatal"}
VALID_PACKAGES_BACKEND = {
    "cache", "controller", "cron_job", "db", "domain",
    "handler", "repository", "route", "service"
}
VALID_PACKAGES_FRONTEND = {"api", "component", "hook", "page", "state", "style"}
VALID_PACKAGES_BOTH = {"auth", "config", "middleware", "utils"}


def Log(stack, level, package, message):
    if stack not in VALID_STACKS:
        print(f"[LOG ERROR] Invalid stack: '{stack}'")
        return None
    if level not in VALID_LEVELS:
        print(f"[LOG ERROR] Invalid level: '{level}'")
        return None
    if stack == "backend":
        allowed_packages = VALID_PACKAGES_BACKEND | VALID_PACKAGES_BOTH
    else:
        allowed_packages = VALID_PACKAGES_FRONTEND | VALID_PACKAGES_BOTH
    if package not in allowed_packages:
        print(f"[LOG ERROR] Invalid package: '{package}' for stack '{stack}'")
        return None

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
    try:
        response = requests.post(LOG_API_URL, json=body, headers=headers)
        if response.status_code in (200,201):
            data = response.json()
            print(f"[LOG SUCCESS] logID: {data.get('logID')} | {stack} | {level} | {package} | {message}")
            return data
        else:
            print(f"[LOG FAILED] Status: {response.status_code} | Response: {response.text}")
            return None
    except Exception as e:
        print(f"[LOG EXCEPTION] Could not send log: {e}")
        return None


if __name__ == "__main__":
    Log("backend", "info", "db", "Database connection established successfully")
    Log("backend", "error", "handler", "Received string, expected bool")
    Log("backend", "fatal", "db", "Critical database connection failure")
