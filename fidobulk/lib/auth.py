import re, requests

def construct_token_request(client_id, client_secret):
    return {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://graph.microsoft.com/.default"
    }

def get_access_token(client_id, client_secret, token_endpoint):
    token_endpoint = f"{token_endpoint}"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    body = construct_token_request(client_id, client_secret)
    try:
        response = requests.post(token_endpoint, data=body, headers=headers, verify=True, timeout=5)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print("Status code:", response.status_code)
        print("Response text:", response.text)
        raise

    token_match = re.search('"access_token":"([^"]+)"', str(response.content))
    if not token_match:
        raise ValueError("Access token not found in response")
    return token_match.group(1)
