import requests

def set_http_headers(access_token):
    return {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }

def fetch_users_in_group(access_token, group_name):
    group_id = fetch_group(access_token=access_token, group_name=group_name)
    groups_endpoint = "https://graph.microsoft.com/beta/groups/" + group_id + "/members"
    
    headers = set_http_headers(access_token)
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
    headers = set_http_headers(access_token)

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

def create_and_activate_fido_method(
        credential_id,
        client_extensions,
        user_name,
        attestation,
        client_data,
        serial_number,
        access_token,
):
    print("-----")
    print("in create_and_activate_fido_method\n")

    headers = set_http_headers(access_token)

    fido_credentials_endpoint = (
            "https://graph.microsoft.com/beta/users/"
            + user_name
            + "/authentication/fido2Methods"
    )

    body = {
        "publicKeyCredential": {
            "id": credential_id,
            "response": {
                "attestationObject": attestation,
                "clientDataJSON": client_data,
            },
            "clientExtensionResults": json.loads(
                base64.b64decode(client_extensions + "=" * (-len(client_extensions) % 4)).decode("utf-8")), },
        # EntraId restricts len(displayName) to 30 characters
        "displayName": (str(serial_number)
                        + " "
                        + str(datetime.date.today()))[:30],
    }

    response = requests.post(
        fido_credentials_endpoint, json=body, headers=headers, verify=False
    )

    if response.status_code == 201:
        create_response = response.json()
        print("\tRegistration success.")
        print(f'\tAuth method objectId: {create_response["id"]}')
        return True, create_response["id"]
    else:
        print(response.status_code)
        print(response.content)
        return False, []