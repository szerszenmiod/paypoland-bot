import re

def validate_crypto_address(crypto_type, address):
    patterns = {
        'LTC': [
            r'^L[a-km-zA-HJ-NP-Z1-9]{25,34}$',
            r'^M[a-km-zA-HJ-NP-Z1-9]{25,34}$',
            r'^ltc1[a-z0-9]{39,59}$'
        ],
        'BTC': [
            r'^1[a-km-zA-HJ-NP-Z1-9]{25,34}$',
            r'^3[a-km-zA-HJ-NP-Z1-9]{25,34}$',
            r'^bc1[a-z0-9]{39,59}$'
        ],
        'ETH': [
            r'^0x[a-fA-F0-9]{40}$'
        ]
    }
    if crypto_type not in patterns:
        return False
    for pattern in patterns[crypto_type]:
        if re.match(pattern, address):
            return True
    return False
