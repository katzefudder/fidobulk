import requests

def fetch_users(access_token):
    url = 'http://localhost:4711/graphql'
    query = """query { users { id displayName email } }"""
    headers = {
        'Authorization': f"Bearer {access_token}",
        'Content-Type': 'application/json'
    }
    response = requests.post(url, json={'query': query}, headers=headers)
    response.raise_for_status()
    return response.json()['data']['users']
