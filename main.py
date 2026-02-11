from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from routes import bridge, interfaces,hotspot,wan, dhcp
from dotenv import load_dotenv
import os

app = FastAPI(title="MIKROTIK API", version="1.0.0")

load_dotenv()

MIKROTIK_HOST = os.getenv("MIKROTIK_HOST")
MIKROTIK_USER = os.getenv("MIKROTIK_USER")
MIKROTIK_PASS = os.getenv("MIKROTIK_PASS")

app.include_router(bridge.router)
app.include_router(interfaces.router)
app.include_router(hotspot.router)
app.include_router(wan.router)
app.include_router(dhcp.router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # During dev, allow all origins
    allow_credentials=True,
    allow_methods=["*"],            # GET, POST, etc.
    allow_headers=["*"],            # Headers like Content-Type
)




@app.get("/")
def test_api():
    return {"info": "Mikrotik API is running!"}