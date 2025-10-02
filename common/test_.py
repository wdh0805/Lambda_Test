import json
import os

import requests
JWT_ALGORITHM = "HS256"

import jwt


SECRET_KEY = "django-insecure-%(@z@+0$-x1r9!j8uh%!rtv^fs!(^+8l-lr5u!u8^z^qc(l6m!"


def get_user_from_token(token: str):
    """
    토큰에서 user_id 추출
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload.get("user_id")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    

def login():
    # body = json.loads(event.get("body") or "{}")
    # login_id = body.get("login_id")
    # password = body.get("password")
    login_id = "testpkorea"
    password = "test1234"
    api_url = "http://52.78.168.191"
    url = f"{api_url}/api/user/login/"
    payload = {"login_id":login_id,"password":password}

    res = requests.post(url=url, json=payload)
    data = res.json()

    # result_code 확인
    if data.get("result_code") != '0':
        return data.get("result_code")
    
    access = data.get("access")
    refresh = data.get("refresh")
    user_id = get_user_from_token(access)
    print(access)
    print(refresh)
    print(user_id)
    
    return {
        "statusCode": res.status_code,
        "body": json.dumps(data)  # 직렬화된 문자열
    }
if __name__=="__main__":
    login()