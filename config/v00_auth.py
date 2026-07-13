import hashlib
import os

_AUTH_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.v00_auth')
_XOR_KEY = 'CMPF'


def _xor_decode(hex_data):
    raw = bytes.fromhex(hex_data)
    key = _XOR_KEY.encode('utf-8')
    decoded = bytearray()
    for i, b in enumerate(raw):
        decoded.append(b ^ key[i % len(key)])
    return decoded.decode('utf-8')


def _parse_file():
    if not os.path.exists(_AUTH_FILE):
        return {}
    with open(_AUTH_FILE, 'r') as f:
        lines = f.read().strip().split('\n')
    data = {}
    for line in lines:
        if ':' in line:
            k, v = line.split(':', 1)
            data[k.strip()] = v.strip()
    return data


def verify_password(password):
    data = _parse_file()
    stored_hash = data.get('SHA256_PASSWORD')
    if not stored_hash:
        return False
    input_hash = hashlib.sha256(password.encode('utf-8')).hexdigest().upper()
    return input_hash == stored_hash


def get_decoded(key):
    data = _parse_file()
    hex_val = data.get(key)
    if not hex_val:
        return None
    return _xor_decode(hex_val)
