from fastapi import FastAPI

app = FastAPI()

@app.get("/dashboard")
def dashboard():
    return {
        "system": "Genesis Payments",
        "active_users": 128,
        "online": True,
        "balance": 452.75
    }
