import json

def _base(body:dict, status=200)->dict:
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"  # CORS 허용
        },
        "body": json.dumps(body)
    }

def ok(data)->dict:
    return _base(data, 200)

def created(data)->dict:
    return _base(data, 201)

def error(message:str, status:int=400)->dict:
    return _base({"message": message}, status)
