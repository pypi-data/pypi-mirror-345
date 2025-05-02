import base64


def atob(s):
    return base64.b64decode(s).decode('utf-8')


def btoa(s):
    return base64.b64encode(s.encode('utf-8')).decode('latin-1')
