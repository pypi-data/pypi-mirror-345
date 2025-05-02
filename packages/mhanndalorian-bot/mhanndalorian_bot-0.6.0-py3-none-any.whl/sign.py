import time
import hashlib
import hmac
from json import dumps

api_key = 'usergeneratedoNtGtKG0YW6sLSj1Q12Q7hOCVhTAgvd0xMexdLK4qZZhnQbSO1'


def update_hmac(hmac_obj: hmac.HMAC, update_items: list) -> hmac.HMAC:
    """Add update_items to hmac_obj and return hmac_obj."""
    print(f"HMAC Hexdigest (base):        {hmac_obj.hexdigest()}")
    for item in update_items:
        hmac_obj.update(item.encode())
        print
    return hmac_obj


def sign(method: str, endpoint: str, payload: dict = None, timestamp: str = None,):
    """HMAC signing function for Mhanndalorian Bot APIs."""
    if timestamp:
        req_time = timestamp
    else:
        req_time = str(int(time.time() * 1000))
    print(f"{req_time=}")
    hmac_obj = hmac.new(key=api_key.encode(), digestmod=hashlib.sha256)
    print(f"HMAC Hexdigest (base):        {hmac_obj.hexdigest()}")
    hmac_obj.update(req_time.encode())
    print(f"HMAC Hexdigest (timestamp):   {hmac_obj.hexdigest()}")
    hmac_obj.update(method.upper().encode())
    print(f"HMAC Hexdigest (HTTP method): {hmac_obj.hexdigest()}")
    hmac_obj.update(endpoint.lower().encode())
    print(f"HMAC Hexdigest (endpoint):    {hmac_obj.hexdigest()}")
    payload_str = dumps(payload or {"payload": {"allyCode": "314927874"}}, separators=(',', ':'))
    print(f"{payload_str=}")
    payload_hash = hashlib.md5(payload_str.encode()).hexdigest()
    print(f"{payload_hash=}")
    hmac_obj.update(payload_hash.encode())
    return {"x-timestamp": req_time, "Authorization": hmac_obj.hexdigest()}


def hmac_sign(api_key: str, method: str, endpoint: str, payload: dict) -> dict[str, str]:
    """HMAC signing function for Mhanndalorian Bot APIs.
    
        Args
            api_key: The API key assigned by Mhanndalorian Bot
            method: The HTTP method of the request
            endpoint: The API endpoint URI
            payload: Dictionary containing the payload of the HTTP request

        Returns
            Dictionary containing the 'x-timestamp' and 'Authorization' headers for the signed request
    """
    # Get the current time in milliseconds
    req_time = str(int(time.time() * 1000))

    # Create a base HMAC object using SHA256 algorithm
    hmac_obj = hmac.new(key=api_key.encode(), digestmod=hashlib.sha256)

    # Add the request timestamp to the HMAC object
    hmac_obj.update(req_time.encode())

    # Add the HTTP method (in upper case) to the HMAC object
    hmac_obj.update(method.upper().encode())

    # Add the API endpoint URI to the HMAC object
    hmac_obj.update(endpoint.lower().encode())

    # Create a serialized string from the payload JSON/dictionary object
    payload_str = dumps(payload, separators=(',', ':'))

    # Generate MD5 hash of the payload string
    payload_hash = hashlib.md5(payload_str.encode()).hexdigest()

    # Add the payload MD5 hash to the HMAC object
    hmac_obj.update(payload_hash.encode())

    # Return the HTTP headers that must be included with the HMAC signed request
    return {"x-timestamp": req_time, "Authorization": hmac_obj.hexdigest()}
