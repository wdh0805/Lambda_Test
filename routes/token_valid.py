import json
import jwt
from common import response
from jwt import ExpiredSignatureError, InvalidTokenError
from datetime import datetime, timezone

from routes import db

SECRET_KEY = "django-insecure-%(@z@+0$-x1r9!j8uh%!rtv^fs!(^+8l-lr5u!u8^z^qc(l6m!"

def verify_jwt(event):
    body             = json.loads(event.get("body", "{}"))
    token            = body.get("token", "Unnamed")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        
        # # user_id 확인
        # if payload.get("user_id") != expected_user_id:
        return_data = db.get_data(user_id=payload.get("user_id"))
        if return_data == "1":
            return response.error(f"Invalid ID",500)
        # 만료 시간 변환
        exp_timestamp = payload.get("exp")
        exp_time = None
        # if exp_timestamp:
        #     exp_time = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)

        return_data =  {
            "success": True,
            "payload": payload,
            "db_data": return_data,
            "expires_at": exp_time.isoformat() if exp_time else None
        }
                
        return response.ok(return_data)
    
    except ExpiredSignatureError:
        return response.error("token_expired", 500)

    except InvalidTokenError:
        return response.error("invalid_token", 500)

