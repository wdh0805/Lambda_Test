import json

def _base(body, status=200):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"  # CORS 허용
        },
        "body": json.dumps(body)
    }

def ok(data):
    return _base(data, 200)

def created(data):
    return _base(data, 201)

def error(message, status=400):
    return _base({"message": message}, status)
