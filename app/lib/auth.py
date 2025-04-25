import re, requests

def construct_token_request(client_id, client_secret):
    return {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://graph.microsoft.com/.default",
    }

def get_access_token(client_id, client_secret, tenant_id):
    # token_endpoint = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    token_endpoint = f"http://localhost:4000/auth/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    body = construct_token_request(client_id, client_secret)
    response = requests.post(token_endpoint, data=body, headers=headers, verify=False)
    response.raise_for_status()
    token_match = re.search('"access_token":"([^"]+)"', str(response.content))
    if not token_match:
        raise ValueError("Access token not found in response")
    return token_match.group(1)
