import json
from google.cloud import secretmanager

def get_api_keys_from_secret(project_id: str, secret_id: str) -> list:
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    
    response = client.access_secret_version(request={"name": name})
    secret_payload = response.payload.data.decode("UTF-8")

    return json.loads(secret_payload)

# Thay bằng ID thật của project và secret
PROJECT_ID = "creator-dev-453406"
SECRET_ID = "apify-fb-keys"

API_KEYS = get_api_keys_from_secret(PROJECT_ID, SECRET_ID)
