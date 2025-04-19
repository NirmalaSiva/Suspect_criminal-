import requests
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import json

SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']
SERVICE_ACCOUNT_FILE = 'your-service-account-file.json'

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
credentials.refresh(Request())
access_token = credentials.token

project_id = 'your-fire-project'
url = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json; UTF-8",
}

message = {
    "message": {
        "topic": "criminal_alerts",
        "data": {
            "title": "Criminal Detected!",
            "message": "A criminal has been identified.",
            "name": "John Doe",
            "date": "2025-04-09",
            "time": "10:32 AM",
            "image": "https://yourserver.com/suspect_image.jpg"
        }
    }
}


response = requests.post(url, headers=headers, data=json.dumps(message))
print("Status Code:", response.status_code)
print("Response:", response.json())
