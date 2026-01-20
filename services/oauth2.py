import os

from google.auth.transport import requests
from google.oauth2 import id_token
from google_auth_oauthlib.flow import InstalledAppFlow

from ui.app import data_dir_path

os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

SCOPES = ["openid", "email", "profile"]

client_path = data_dir_path + "oauth_client.json"

def google_login():
    flow = InstalledAppFlow.from_client_secrets_file(
        client_path,
        SCOPES
    )

    cred = flow.run_local_server(port=0, success_message="Login successful, Returning to application...")

    return get_user_data(cred)

def get_user_data(cred):
    info = id_token.verify_oauth2_token(
        cred.id_token,
        requests.Request(),
    )

    return {
        "user_id": info["sub"],
        "email": info.get("email"),
        "name": info.get("name"),
    }
