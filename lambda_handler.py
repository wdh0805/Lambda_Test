import json
from routes import db, users, jobs
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
        # 별칭 구분하여 API 요청하는 곳을 다르게 함
        # 예: arn:aws:lambda:ap-northeast-2:123456789012:function:LambdaTest:prod
        alias = context.invoked_function_arn.split(":")[-1]
        if alias == "prod":
            api_url = "http://shopback.3dons.net"
        else:
            api_url = "https://52.78.168.191"  # 오타 수정됨

        http = (event.get("requestContext") or {}).get("http") or {}
        method = http.get("method", "GET")
        path = _norm_path(event)  # 예: "/users", "/jobs", "/token"

        # 라우트 매핑
        routes = {
            ("GET", "/users"): users.list_users,
            ("POST", "/jobs"): jobs.create_job,
            ("POST", "/db_create"): db.put_data,
            ("POST", "/login"): (users.login,{"api_url":api_url})
        }

        handler = routes.get((method, path))
        if handler:
            # api_url을 함수에 전달하도록 변경
            return handler(event, api_url=api_url)
        else:
            return response.error("Not Found", 404)

    except Exception as e:
        # 운영환경에서는 내부 에러 메시지 노출하지 않음
        return response.error("Internal Error", 500)
