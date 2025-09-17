import json
import boto3
from common import response  # 응답 헬퍼 사용

TABLE_NAME = "Lambda_with_DB"

def put_data(event, context=None):
    dynamodb = boto3.client("dynamodb")

    body = json.loads(event.get("body") or "{}")
    user_id = body.get("user_id")
    available_yn = body.get("available_YN")

    if not user_id or not available_yn:
        return response.error("user_id, available_YN 둘 다 필요합니다.", 400)

    # 기본키 + 다양한 타입의 예시 속성 포함
    item = {
        "User": {"S": user_id},                # PK(테이블의 파티션 키 이름과 동일해야 함)
        "Available_YN": {"S": available_yn},   # (테이블에 정렬 키가 없다면 이 줄은 제거)
    }

    try:
        put_resp = dynamodb.put_item(          # 변수명 충돌 방지
            TableName=TABLE_NAME,
            Item=item                           # 대문자 Item
        )
        return response.ok({
            "ok": True,
            "key": {"User": user_id, "Available_YN": available_yn}
        })
    except Exception as e:
        return response.error(str(e), 500)

def get_data(user_id:str)->str:
    dynamodb = boto3.client("dynamodb")

    try:
        resp = dynamodb.get_item(
            TableName=TABLE_NAME,
            Key={"User": {"S": str(user_id)}}
        )
        item = resp.get("Item")
        if not item:
            return "500"

        if item.get("Available_YN", {}).get("S") == "Y":
            return "0" 
        else:
            return "500"

    except Exception:
        return "500"