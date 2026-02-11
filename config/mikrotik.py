from routeros_api import RouterOsApiPool
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

MIKROTIK_HOST = os.getenv("MIKROTIK_HOST")
MIKROTIK_USER = os.getenv("MIKROTIK_USER")
MIKROTIK_PASS = os.getenv("MIKROTIK_PASS")

def get_mikrotik_api():
    return RouterOsApiPool(
        MIKROTIK_HOST,
        username=MIKROTIK_USER,
        password=MIKROTIK_PASS,
        plaintext_login=True
    )
