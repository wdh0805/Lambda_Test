import uuid
import jwt
from datetime import datetime, timezone, timedelta
import os

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_LIFETIME = timedelta(hours=1)
REFRESH_TOKEN_LIFETIME = timedelta(hours=1, minutes=30)
SECRET_KEY = os.getenv("TOKEN_KEY")

def create_access_token(user_id: str)->str:
    """
        access token 생성
    """
    now = datetime.now(timezone.utc)
    exp = now + ACCESS_TOKEN_LIFETIME

    payload = {
        "token_type": "access",
        "exp": int(exp.timestamp()),   # 유닉스 타임스탬프
        "iat": int(now.timestamp()),   # 발급 시간
        "jti": uuid.uuid4().hex,       # 고유 토큰 ID
        "user_id": user_id,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)

def create_refresh_token(user_id: int)->str:
    """
        refresh token 생성
    """
    now = datetime.now(timezone.utc)
    exp = now + REFRESH_TOKEN_LIFETIME

    payload = {
        "token_type": "refresh",
        "exp": int(exp.timestamp()),
        "iat": int(now.timestamp()),
        "jti": uuid.uuid4().hex,
        "user_id": user_id,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)

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
    
def is_valid_token(token: str, expected_type: str = "access") -> bool:
    """
    토큰 검증 함수
    expected_type:
        - "access"  → Access 토큰 검증
        - "refresh" → Refresh 토큰 검증
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload.get("token_type") == expected_type
    
    except jwt.ExpiredSignatureError:   # 만료 토큰
        return False
    
    except jwt.InvalidTokenError:   # 비정상 토큰
        return False
    
if __name__=="__main__":
    pass