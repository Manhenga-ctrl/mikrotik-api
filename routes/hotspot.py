from fastapi import APIRouter, HTTPException,APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from schemas.hotspot import BulkCreateByCount
from mikrotik import MIKROTIK_HOST, get_mikrotik_api

import random
import string


router = APIRouter(prefix="/hotspot", tags=["Hotspot"])


# This endpoint lists all Hotspot servers on the MikroTik router
@router.get("/users")
def list_hotspot_users():
    api_pool = get_mikrotik_api()
    api = api_pool.get_api()

    try:
        hotspot_users = api.get_resource("/ip/hotspot/user").get()

        users_list = []
        for user in hotspot_users:
            users_list.append({
                "username": user.get("name"),
                "mac_address": user.get("mac-address"),
                "ip_address": user.get("address"),
                "rx_bytes": int(user.get("bytes-in", 0)),
                "tx_bytes": int(user.get("bytes-out", 0)),
                "uptime": user.get("uptime", "0s"),
                "profile": user.get("profile"),
                "disabled": user.get("disabled") == "true"
            })

        return {"total_users": len(users_list), "users": users_list}

    finally:
        api_pool.disconnect()



# This endpoint lists all active Hotspot users on the MikroTik router
@router.get("/active")
def list_active_hotspot_users():
    api_pool = get_mikrotik_api()
    api = api_pool.get_api()

    try:
        active_users = api.get_resource("/ip/hotspot/active").get()

        users_list = []
        for user in active_users:
            users_list.append({
                "username": user.get("user"),
                "mac_address": user.get("mac-address"),
                "ip_address": user.get("address"),
                "rx_bytes": int(user.get("bytes-in", 0)),
                "tx_bytes": int(user.get("bytes-out", 0)),
                "uptime": user.get("uptime", "0s"),
                "profile": user.get("profile"),
                "disabled": user.get("disabled") == "true"
            })

        return {"total_active_users": len(users_list), "active_users": users_list}

    finally:
        api_pool.disconnect()



#This endpoint is for creating a new Hotspot user on the MikroTik router
class HotspotUserCreateRequest(BaseModel):
    name: str
    password: str
    profile: str
    disabled: bool = False


@router.post("/users/create")
def create_hotspot_user(user: HotspotUserCreateRequest):
    api_pool = get_mikrotik_api()
    api = api_pool.get_api()

    try:
        hotspot_user_resource = api.get_resource("/ip/hotspot/user")
        hotspot_user_resource.add(
            name=user.name,
            password=user.password,
            profile=user.profile,
            disabled="true" if user.disabled else "false"
        )
        return {"success": True, "message": f"Hotspot user '{user.name}' created successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        api_pool.disconnect()



# This endpoint gives list of hotspot profiles
@router.get("/profiles")
def list_hotspot_profiles():
    api_pool = get_mikrotik_api()
    api = api_pool.get_api()

    try:
        hotspot_profiles = api.get_resource("/ip/hotspot/profile").get()

        profiles_list = []
        for profile in hotspot_profiles:
            profiles_list.append({
                "name": profile.get("name"),
                "idle_timeout": profile.get("idle-timeout"),
                "shared_users": profile.get("shared-users"),
                "rate_limit": profile.get("rate-limit"),
            })

        return {"total_profiles": len(profiles_list), "profiles": profiles_list}

    finally:
        api_pool.disconnect()

# This endpoint is for creating a new Hotspot profile on the MikroTik routerclass HotspotDeleteRequest(BaseModel

class HotspotProfileCreateRequest(BaseModel):
    name: str
    rate_limit: str = None        # e.g., "1M/1M"
    session_timeout: str = None   # e.g., "1h"
    shared_users: int = 1    







@router.post("/profiles/create")

def create_hotspot_profile(profile: HotspotProfileCreateRequest):
    api_pool = get_mikrotik_api()
    api = api_pool.get_api()

    try:
        hotspot_profiles = api.get_resource('/ip/hotspot/user/profile')

        # Check if profile already exists
        existing = next((p for p in hotspot_profiles.get() if p.get('name') == profile.name), None)
        if existing:
            raise HTTPException(status_code=400, detail=f"Profile '{profile.name}' already exists.")

        # Add profile
        hotspot_profiles.add(
            name=profile.name,
            rate_limit=profile.rate_limit or "",
            session_timeout=profile.session_timeout or "",
            shared_users=str(profile.shared_users)
        )

        return {"success": True, "message": f"Hotspot profile '{profile.name}' created successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        api_pool.disconnect()





@router.get("/users/all")
def list_all_hotspot_users():
    api_pool = get_mikrotik_api()
    api = api_pool.get_api()
    try:
        users_resource = api.get_resource("/ip/hotspot/user")
        users = users_resource.get()
        
        # Convert rx/tx bytes to int for consistency
        result = []
        for u in users:
            result.append({
                "username": u.get("name"),
                "mac_address": u.get("mac-address"),
                "ip_address": u.get("address", "N/A"),  # some inactive users may not have IP
                "rx_bytes": int(u.get("bytes-in", 0)),
                "tx_bytes": int(u.get("bytes-out", 0)),
                "profile": u.get("profile"),
                "disabled": u.get("disabled", False)
            })
        return {"total_users": len(result), "users": result}
    finally:
        api_pool.disconnect()





@router.get("/ip-bindings")
def list_ip_bindings():
    try:
        connection = get_mikrotik_api()
        api = connection.get_api()

        bindings = api.get_resource("/ip/hotspot/ip-binding").get()

        result = []
        for b in bindings:
            result.append({
                "id": b.get(".id"),
                "ip": b.get("address"),
                "mac": b.get("mac-address"),
                "type": b.get("type"),        # bypassed / blocked / regular
                "comment": b.get("comment"),
                "disabled": b.get("disabled", False)
            })

        return {
            "count": len(result),
            "bindings": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        try:
            connection.disconnect()
        except:
            pass



@router.get("/server/profiles")
def list_hotspot_profiles():
    api_pool = get_mikrotik_api()
    api = api_pool.get_api()
    try:
        profiles_resource = api.get_resource("/ip/hotspot/user/profile")
        profiles = profiles_resource.get()  # fetch all hotspot profiles

        result = []
        for p in profiles:
            result.append({
                "name": p.get("name"),
                "rate_limit": p.get("rate-limit", "N/A"),
                "session_timeout": p.get("session-timeout", "N/A"),
                "shared_users": p.get("shared-users", "N/A"),
                "address_pool": p.get("address-pool", "N/A")
            })

        return {"total_profiles": len(result), "profiles": result}
    finally:
        api_pool.disconnect()


# THIS END POINT IS FOR SHOWING FILES ON THE MIKROTIK ROUTER

@router.get("/files/all")
def list_mikrotik_files():
    api_pool = get_mikrotik_api()
    api = api_pool.get_api()
    try:
        files_resource = api.get_resource("/file")
        files = files_resource.get()  # get all files on the device

        result = []
        for f in files:
            result.append({
                "name": f.get("name"),
                "size": int(f.get("size", 0)),
                "type": f.get("type"),
                "creation_time": f.get("creation-time"),
                "last_modified": f.get("last-modified")
            })

        return {"total_files": len(result), "files": result}
    finally:
        api_pool.disconnect()






@router.put("/{username}/disable")
def disable_hotspot_user(username: str):
    api_pool = get_mikrotik_api()
    api = api_pool.get_api()

    try:
        users = api.get_resource("/ip/hotspot/user")
        all_users = users.get()

        user = next((u for u in all_users if u.get("name") == username), None)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user_id = user.get(".id")
        users.set(id=user_id, disabled="yes")

        return {
            "success": True,
            "message": f"User '{username}' disabled"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



def generate_password(length: int):
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


@router.post("/users/bulk-create")
def bulk_create_users(data: BulkCreateByCount):
    api_pool = get_mikrotik_api()
    api = api_pool.get_api()
    user_resource = api.get_resource("/ip/hotspot/user")

    created_users = []

    for i in range(data.count):
        username = f"{data.username_prefix}{random.randint(100000, 999999)}"
        password = generate_password(data.password_length)

        try:
            user_resource.add(
                name=username,
                password=password,
                profile=data.profile
            )

            created_users.append({
                "username": username,
                "password": password,
                "profile": data.profile
            })

        except Exception as e:
            continue  # skip duplicates safely

    return {
        "created": len(created_users),
        "users": created_users
    }






@router.get("/files")
def list_hotspot_files():
    api_pool = get_mikrotik_api()
    api = api_pool.get_api()

    ALLOWED_FILES = {
        "login.html",
        "logout.html",
        "status.html",
        "error.html",
        "alogin.html",
        "redirect.html",
        "trial.html",
        "ads.html",
        "radvert.html",
        "style.css",
        "favicon.ico",
    }

    try:
        files_resource = api.get_resource("/file")
        files = files_resource.get()

        result = []

        for f in files:
            name = f.get("name", "")

            # Must be directly under hotspot/
            if not name.startswith("hotspot/"):
                continue

            # Remove hotspot/
            short_name = name.replace("hotspot/", "", 1)

            # ❌ Skip subfolders (img/, js/, etc.)
            if "/" in short_name:
                continue

            # ✅ Only explicitly allowed files
            if short_name in ALLOWED_FILES:
                result.append({
                    "name": short_name,
                    "path": name,
                    "size": int(f.get("size", 0)),
                    "type": f.get("type"),
                })

        return {
            "total_files": len(result),
            "files": result,
        }

    finally:
        api_pool.disconnect()




