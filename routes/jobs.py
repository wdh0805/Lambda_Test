import json
from common import response

def create_job(event):
    body = json.loads(event.get("body", "{}"))
    name = body.get("name", "Unnamed")

    result = {
        "job_id": 123,
        "name": name,
        "status": "created"
    }
    return response.created(result)
