import requests
import logging

def submit_user_data(user, pin_value, serial, config):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    backend_config = config['backend']
    
    protocol = backend_config['protocol']
    host = backend_config['host']
    port = backend_config['port']
    endpoint = backend_config['endpoint']
    url = f"{protocol}://{host}:{port}{endpoint}"
    payload = {
        "user": user['displayName'],
        "serial_number": serial,
        "pin": pin_value, 
        "message": "lorem ipsum"
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"❌ Ein Fehler ist aufgetreten: {http_err}")
        raise
