from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
from mikrotik import get_active_users


app = FastAPI(title="Hotspot Controller API")

# Allow frontend to access API (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)




# Simple API endpoint
@app.get("")
def hello():
    return {"message": "System is online and ready to serve!"}


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

