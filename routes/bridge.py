from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from mikrotik import get_mikrotik_api


router = APIRouter(prefix="/bridge", tags=["Bridge"])

class BridgeCreateRequest(BaseModel):
    name: str
    mtu: int = 1500
    protocol_mode: str = "none"  # options: none, stp, rstp
    arp: str = "enabled"         # options: enabled, disabled, proxy-arp, reply-only

class BridgeDeleteRequest(BaseModel):
    name: str




@router.get("/list")
def list_bridges():
    api_pool = get_mikrotik_api()
    api = api_pool.get_api()
    try:
        bridge_resource = api.get_resource("/interface/bridge")
        bridges = bridge_resource.get()
        bridge_list = []
        for bridge in bridges:
            bridge_list.append({
                "name": bridge.get("name"),
                "mtu": bridge.get("mtu"),
                "admin_mac": bridge.get("admin-mac"),
                "protocol_mode": bridge.get("protocol-mode"),
                "priority": bridge.get("priority"),
                "running": bridge.get("running") == "true",
                "arp": bridge.get("arp")
            })
        return {"total_bridges": len(bridge_list), "bridges": bridge_list}
    finally:
        api_pool.disconnect()



@router.post("/create")
def create_bridge(bridge: BridgeCreateRequest):
    api_pool = get_mikrotik_api()
    api = api_pool.get_api()
    try:
        bridge_resource = api.get_resource("/interface/bridge")
        bridge_resource.add(
            name=bridge.name,
            mtu=str(bridge.mtu),
            protocol_mode=bridge.protocol_mode,
            arp=bridge.arp
        )
        return {"success": True, "message": f"Bridge '{bridge.name}' created successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        api_pool.disconnect()



# This endpoint deletes a bridge by name

@router.post("/delete")
def delete_bridge(bridge: BridgeDeleteRequest):
    api_pool = get_mikrotik_api()
    api = api_pool.get_api()

    try:
        bridge_resource = api.get_resource("/interface/bridge")
        bridges = bridge_resource.get()

        # Find the bridge by name
        bridge_to_delete = next((b for b in bridges if b.get('name') == bridge.name), None)
        if not bridge_to_delete:
            raise HTTPException(status_code=404, detail=f"Bridge '{bridge.name}' not found.")

        # Delete using filter by name (works even if '.id' is missing)
        bridge_resource.remove(**{'name': bridge.name})
        return {"success": True, "message": f"Bridge '{bridge.name}' deleted successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        api_pool.disconnect()
