import json
from common import response
import requests
from requests import Response
import boto3
from common.constant import DYNAMODB_NAME
from common.token import create_access_token, get_user_from_token, is_valid_token

def echo(event:dict, api_url:str): 
    print("echo test start")
    body = json.loads(event.get("body") or "{}")

    echo_result_code:str = body.get("echo_result_code")
    echo_result_desc:str = body.get("echo_result_desc")

    url    :str  = f"{api_url}/api/system/echo/"
    payload:dict = {
            'echo_result_code'   : echo_result_code,
            'echo_result_desc'   : echo_result_desc,
        }

    print("echo test to shop start")
    res:Response = requests.post(url=url, json=payload)
    print("echo test to shop end")
    data = res.json()

    print("echo test end")
    return response.ok(data=data)

def refresh_token(event:dict):
    print("refresh token start")
    body = json.loads(event.get("body") or "{}")
    refresh_token = body.get("refresh")

    if is_valid_token(token=refresh_token, expected_type="refresh"):
        user          = str(get_user_from_token(refresh_token))
        access_token  = create_access_token(user)           # access token 생성
        refresh_token = create_access_token(user)           # refresh token 생성
        register_user(refresh=refresh_token, user_id=user)  # 데이터 등록
        data = {"access":access_token, "refresh":refresh_token}
        print("refresh token end")
        return response.ok(data=data)

    else:
        print("refresh token error")
        return response.error(message="invalid token")

def register_user(refresh:str, user_id: str) -> bool:
    print("register user start")
    try:
        dynamodb = boto3.client("dynamodb")
        # 기존 데이터 확인
        resp = dynamodb.get_item(
            TableName=DYNAMODB_NAME,
            Key={"User": {"S": user_id}}
        )
        item = resp.get("Item")

        if item:
            # 기존 데이터 있으면 refresh 토큰만 업데이트
            dynamodb.update_item(
                TableName=DYNAMODB_NAME,
                Key={"User": {"S": user_id}},
                UpdateExpression="SET refresh = :r",
                ExpressionAttributeValues={":r": {"S": refresh}},
                ReturnValues="UPDATED_NEW"
            )
            print(f"update existing user : {user_id}")
        else:
            # 기존 데이터 없으면 새로 저장
            dynamodb.put_item(
                TableName=DYNAMODB_NAME,
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
    dynamodb = boto3.client("dynamodb")
    response = dynamodb.scan(TableName=DYNAMODB_NAME)
    items = response.get("Items", [])

    while "LastEvaluatedKey" in response:
        response = dynamodb.scan(
            TableName=DYNAMODB_NAME,
            ExclusiveStartKey=response["LastEvaluatedKey"]
        )
        items.extend(response.get("Items", []))

    for item in items:
        user_id = item["User"]["S"]
        refresh_token = item["refresh"]["S"]
        if not is_valid_token(token=refresh_token,expected_type="refresh"):
            dynamodb.delete_item(
                TableName=DYNAMODB_NAME,
                Key={"User": {"S": str(user_id)}}
            )
            print(f"deleted_user : {user_id}")
    print("cleanup user end")
    