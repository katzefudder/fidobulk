import requests

def fetch_users_in_group(access_token, group_name):
    group_id = fetch_group(access_token=access_token, group_name=group_name)
    groups_endpoint = "https://graph.microsoft.com/beta/groups/" + group_id + "/members"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    params = {"$select": "id,email,displayName"}
    response = requests.get(
        groups_endpoint, headers=headers, params=params, verify=True
    )
    if response.status_code == 200:
        members = response.json()["value"]
        return members
    else:
        print(response.status_code)
        print(response.content)
        return None

def fetch_group(access_token, group_name):
    headers = {
        'Authorization': f"Bearer {access_token}",
        'Content-Type': 'application/json'
    }

    groups_endpoint = "https://graph.microsoft.com/beta/groups/"
    params = {
        "$filter": "displayName eq '" + group_name + "'"
    }
    response = requests.get(
        groups_endpoint, headers=headers, params=params, verify=True
    )
    if response.status_code == 200:
        group_id = response.json()["value"][0]["id"]
        return group_id
    else:
        print(response.status_code)
        print(response.content)
        return None