from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
from mikrotik import get_active_users, create_hotspot_user
from pydantic import BaseModel



app = FastAPI(title="Hotspot Controller API")

# Allow frontend to access API (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)




# Simple API endpoint
@app.get("/hello")
def hello():
    return {"message": "Hello, World!"}


@app.get("/active")
def dashboard():
    """Summary endpoint for dashboard"""
    active = get_active_users()
    return {
        "system": "GENESIS",
        "online": True,
        "active_users_count": len(active),
        "active_users": active
    }


# Input model for new user
class HotspotUserCreate(BaseModel):
    username: str
    password: str
    profile: str = "default"
    limit_uptime: str = "unlimited"
    comment: str = ""

@app.post("/users/create")
def create_user(data: HotspotUserCreate):
    """Create a new hotspot user on MikroTik"""
    result = create_hotspot_user(
        username=data.username,
        password=data.password,
        profile=data.profile,
        limit_uptime=data.limit_uptime,
        comment=data.comment
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result
