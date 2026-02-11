

from fastapi import APIRouter, HTTPException
from config.mikrotik import MIKROTIK_HOST, get_mikrotik_api

router = APIRouter(prefix="/system", tags=["System Resources"])



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