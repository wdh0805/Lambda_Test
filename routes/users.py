import json
from common import response
import requests
import boto3
from common.token import create_access_token, get_user_from_token, is_valid_token

dynamodb = boto3.client("dynamodb")
TABLE_NAME = "Lambda_with_DB"

def list_users(event):
    data = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "fBob"}
    ]
    return response.ok(data)

def refresh_token(event):
    print("refresh token start")
    body = json.loads(event.get("body") or "{}")
    refresh_token = body.get("refresh")

    if is_valid_token(token=refresh_token, expected_type="refresh"):
        user = str(get_user_from_token(refresh_token))
        access_token = create_access_token(user)    # access token 생성
        refresh_token = create_access_token(user)   # refresh token 생성
        register_user(refresh=refresh_token, user_id=user)   # 데이터 등록
        data = {"access":access_token, "refresh":refresh_token}
        print("refresh token end")
        return response.ok(data=data)

    else:
        print("refresh token end")
        return response.error()

def login(event,api_url:str):
    print("login start")
    body = json.loads(event.get("body") or "{}")
    login_id = body.get("login_id")
    password = body.get("password")

    url = f"{api_url}/api/user/login/"
    payload = {"login_id":login_id,"password":password}

    print("login request to shop start")
    res = requests.post(url=url, json=payload)
    print("login request to shop end")

    data = res.json()

    # result_code 실패
    if data.get("result_code") != '0':
        return response.error(data=data)
    
    access = data.get("access")
    refresh = data.get("refresh")
    user_id = get_user_from_token(access)
    cleanup_dynamodb_user()
    register_user(refresh=refresh, user_id=str(user_id))

    print("login end")
    return response.ok(data=data)

def register_user(refresh:str, user_id: str) -> bool:
    print("register user start")
    try:
        # 기존 데이터 확인
        resp = dynamodb.get_item(
            TableName=TABLE_NAME,
            Key={"User": {"S": user_id}}
        )
        item = resp.get("Item")

        if item:
            # 기존 데이터 있으면 refresh 토큰만 업데이트
            dynamodb.update_item(
                TableName=TABLE_NAME,
                Key={"User": {"S": user_id}},
                UpdateExpression="SET refresh = :r",
                ExpressionAttributeValues={":r": {"S": refresh}},
                ReturnValues="UPDATED_NEW"
            )
            print(f"update existing user : {user_id}")
        else:
            # 기존 데이터 없으면 새로 저장
            dynamodb.put_item(
                TableName=TABLE_NAME,
                Item={
                    "User": {"S": user_id},
                    "refresh": {"S": refresh},
                }
            )
            print(f"create new user : {user_id}")

        print("register user end")
        return True

    except Exception as e:
        print(f"register_user error: {e}")
        return False
    

def cleanup_dynamodb_user():
    print("cleanup user start")
    # 1. 테이블 전체 스캔
    response = dynamodb.scan(TableName=TABLE_NAME)
    items = response.get("Items", [])

    while "LastEvaluatedKey" in response:
        response = dynamodb.scan(
            TableName=TABLE_NAME,
            ExclusiveStartKey=response["LastEvaluatedKey"]
        )
        items.extend(response.get("Items", []))

    for item in items:
        user_id = item["User"]["S"]
        refresh_token = item["refresh"]["S"]
        if not is_valid_token(token=refresh_token,expected_type="refresh"):
            dynamodb.delete_item(
                TableName=TABLE_NAME,
                Key={"User": {"S": str(user_id)}}
            )
            print(f"deleted_user : {user_id}")
    print("cleanup user end")
    