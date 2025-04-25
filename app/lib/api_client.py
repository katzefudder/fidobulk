import requests

def submit_user_data(user, serial):
    url = "http://localhost:5000/api"
    payload = {
        "user": user['displayName'],
        "serial_number": serial,
        "message": "lorem ipsum"
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()
