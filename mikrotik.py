import os
from routeros_api import RouterOsApiPool
from dotenv import load_dotenv

load_dotenv()

def get_active_users():
    """Get currently active hotspot users (online)"""
    api_pool = RouterOsApiPool(
        os.getenv("MT_HOST"),
        username=os.getenv("MT_USER"),
        password=os.getenv("MT_PASSWORD"),
        port=int(os.getenv("MT_PORT")),
        plaintext_login=True
    )
    api = api_pool.get_api()
    hotspot = api.get_resource('/ip/hotspot/active')
    users = hotspot.get()
    api_pool.disconnect()

    return [
        {
            "user": u.get("user"),
            "ip": u.get("address"),
            "mac": u.get("mac-address"),
            "uptime": u.get("uptime"),
            "host": u.get("host")
        }
        for u in users
    ]

