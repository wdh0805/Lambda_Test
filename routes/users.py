from common import response

def list_users(event):
    data = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "fBob"}
    ]
    return response.ok(data)
