from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from config.mikrotik import MIKROTIK_HOST, get_mikrotik_api

router = APIRouter(prefix="/interfaces", tags=["Interfaces"])


#This endpoint lists all network interfaces on the MikroTik router  

@router.get("/list")
def get_interfaces():
    api_pool = get_mikrotik_api()
    api = api_pool.get_api()

    try:
        interfaces = api.get_resource("/interface").get()
        result = []

        for iface in interfaces:
            result.append({
                "name": iface.get("name"),
                "type": iface.get("type"),
                "running": iface.get("running"),
                "disabled": iface.get("disabled")
            })

        return {
            "router": MIKROTIK_HOST,
            "interfaces": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        api_pool.disconnect()

#This Endpoint list all Wireless Interfaces on the MikroTik router

@router.get("/wireless")
def get_wireless_interfaces():
    api_pool = get_mikrotik_api()
    api = api_pool.get_api()

    try:
        wireless_ifaces = api.get_resource("/interface/wireless").get()
        result = []

        for iface in wireless_ifaces:
            result.append({
                "name": iface.get("name"),
                "ssid": iface.get("ssid"),
                "mode": iface.get("mode"),
                "frequency": iface.get("frequency"),
                "running": iface.get("running"),
                "disabled": iface.get("disabled")
            })

        return {
            "router": MIKROTIK_HOST,
            "wireless_interfaces": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        api_pool.disconnect()