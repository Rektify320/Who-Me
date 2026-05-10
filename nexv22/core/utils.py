import base64

def b64fix(data: str) -> str:
    data = data.replace('-', '+').replace('_', '/')
    padding = 4 - len(data) % 4
    if padding != 4:
        data += '=' * padding
    return data

def b64decode(data: str) -> bytes:
    return base64.b64decode(b64fix(data))

def b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()