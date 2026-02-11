from routeros_api import RouterOsApiPool

MIKROTIK_HOST = "10.50.0.2"
MIKROTIK_USER = "admin"
MIKROTIK_PASS = "admin"

def get_mikrotik_api():
    return RouterOsApiPool(
        MIKROTIK_HOST,
        username=MIKROTIK_USER,
        password=MIKROTIK_PASS,
        plaintext_login=True
    )
