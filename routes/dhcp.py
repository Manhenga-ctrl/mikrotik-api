
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from mikrotik import MIKROTIK_HOST, get_mikrotik_api


router = APIRouter(prefix="/dhcp", tags=["DHCP"])



@router.get("/all")
def list_all_dhcp_leases():
    api_pool = get_mikrotik_api()
    api = api_pool.get_api()
    try:
        leases_resource = api.get_resource("/ip/dhcp-server/lease")
        leases = leases_resource.get()

        result = []
        for l in leases:
            result.append({
                "mac_address": l.get("mac-address"),
                "ip_address": l.get("address", "N/A"),
                "status": l.get("status"),
                "host_name": l.get("host-name", "N/A"),
                "last_seen": l.get("last-seen", "N/A")
            })

        return {"total_leases": len(result), "leases": result}

    finally:
        api_pool.disconnect()




# This endpoint lists DHCP client status
@router.get("/dhcp-client")
def get_dhcp_client_status():
    api_pool = get_mikrotik_api()
    api = api_pool.get_api()

    try:
        resource = api.get_resource("/ip/dhcp-client")
        clients = resource.get()

        result = []
        for c in clients:
            result.append({
                "interface": c.get("interface"),
                "status": c.get("status"),
                "ip_address": c.get("address"),
                "gateway": c.get("gateway"),
                "uptime": c.get("uptime"),
                "disabled": c.get("disabled", False)
            })

        return {
            "total_clients": len(result),
            "clients": result
        }

    finally:
        api_pool.disconnect()
