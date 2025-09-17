import json
from routes import db, users, jobs, token_valid
from common import response

def _norm_path(event):
    """스테이지 접두어(/test, /prod)를 제거해 논리 경로로 변환"""
    raw = event.get("rawPath") or "/"
    stage = (event.get("requestContext") or {}).get("stage")
    if stage and raw.startswith("/" + stage):
        trimmed = raw[len(stage) + 1:]  # "/users" 또는 ""
        return trimmed if trimmed else "/"
    return raw

def lambda_handler(event, context):
    try:
        http = (event.get("requestContext") or {}).get("http") or {}
        method = http.get("method", "GET")
        path = _norm_path(event)  # 예: "/users", "/jobs", "/token"

        if method == "GET" and path == "/users":
            return users.list_users(event)

        elif method == "POST" and path == "/jobs":
            return jobs.create_job(event)

        elif method == "POST" and path == "/token":
            return token_valid.verify_jwt(event)
        
        elif method == "POST" and path == "/db_create":
            return db.put_data(event)

        else:
            return response.error("Not Found", 404)

    except Exception as e:
        # 에러 메시지를 노출하고 싶지 않으면 "Internal Error" 등으로 바꾸세요.
        return response.error(str(e), 500)
