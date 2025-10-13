import json
from routes import shop_app, users
from common import response

def _norm_path(event:dict)->str: 
    """스테이지 접두어(/test, /prod)를 제거한 경로로 변환"""
    raw = event.get("rawPath") or "/" 
    stage = (event.get("requestContext") or {}).get("stage") 
    if stage and raw.startswith("/" + stage): 
        trimmed = raw[len(stage) + 1:] # "/users" 또는 "" 
        return trimmed if trimmed else "/" 
    return raw

def lambda_handler(event:dict, context):
    """
        API 입구
        from aws_lambda_typing import context as context_
        context:context_.Context
    """
    print("lambda handler start")
    try:
        # 별칭 구분하여 API 요청하는 곳을 다르게 함
        # 예: arn:aws:lambda:ap-northeast-2:123456789012:function:LambdaTest:prod
        alias = context.invoked_function_arn.split(":")[-1]
        if alias == "prod":
            api_url = "https://shopback.3dons.net"
        else:
            api_url = "http://52.78.168.191"
        print(f"server : {alias}")

        http  :dict = (event.get("requestContext") or {}).get("http") or {}
        method:str  = http.get("method", "GET")
        path  :str  = _norm_path(event) # 예: "/users", "/jobs", "/token"
        print(http)
        print(method)
        print(path)

        routes = {
            # User 관련 API
            ("GET", "/users")     : (users.list_users, {}),
            # ("POST", "/login")    : (users.login, {"api_url": api_url}),
            ("POST", "/refresh")  : (users.refresh_token,{}),

            # APP Server API
            ("POST", "/api/echo/")    : (shop_app.echo, {"api_url": api_url}), # echo test
            # ("POST", "/api/login/SL/"): (shop_app.login_SL, {"api_url": api_url, "server":alias}),
            # ("POST", "/api/login/OL/"): (users.list_users, {}),

        }

        # API 존재 확인 후 실행 
        handler_info = routes.get((method, path))
        if handler_info:
            func, kwargs = handler_info
            return func(event, **kwargs)
        else:
            return response.error("Not Found", 404)

    except Exception as e:
        # 운영환경에서는 내부 에러 메시지 노출하지 않음
        print(e)
        return response.error("Internal Error", 500)
