
from fastapi import APIRouter, HTTPException
from config.mikrotik import  get_mikrotik_api

router = APIRouter(prefix="/wan", tags=["WAN"])


# this route shows the Eth0 interface details
@router.get("/")
def get_wan():
    api_pool = get_mikrotik_api()
    api = api_pool.get_api()

    try:
        routes = api.get_resource("/ip/route").get()
        default = [r for r in routes if r.get("dst-address") == "0.0.0.0/0"]

        return default

    finally:
        api_pool.disconnect()



@router.get("/dhcp-leases")
def get_dhcp_leases():      
    api_pool = get_mikrotik_api()
    api = api_pool.get_api()

    try:
        leases = api.get_resource("/ip/dhcp-server/lease").get()
        return leases

    finally:
        api_pool.disconnect()

@router.get("/cpu")
def get_cpu_usage():
    api_pool = get_mikrotik_api()
    api = api_pool.get_api()

    try:
        cpu_stats = api.get_resource("/system/resource").get()
        if cpu_stats:
            return {
                "cpu_load": cpu_stats[0].get("cpu-load"),
                "uptime": cpu_stats[0].get("uptime"),
                "free_memory": cpu_stats[0].get("free-memory"),
                "total_memory": cpu_stats[0].get("total-memory")
            }
        else:
            raise HTTPException(status_code=404, detail="CPU stats not found")

    finally:
        api_pool.disconnect()