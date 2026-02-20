from fastapi import FastAPI, HTTPException , Depends, HTTPException, status, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from routes import bridge, interfaces,hotspot,wan, dhcp,system
import os
import logging
from datetime import datetime, timedelta
from typing import List
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel, validator
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import uvicorn
from dotenv import load_dotenv

load_dotenv()


app = FastAPI(title="MIKROTIK ROUTER MANAMGEMENT API", version="1.0.0")

# CORS – restrict in production!

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://209.97.148.247",
        "http://209.97.148.247:8000",
        "https://yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)






logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set in environment variables")

ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "mikrotik")  

client = AsyncIOMotorClient(MONGODB_URL)
db = client[DATABASE_NAME]
users_collection = db["users"]
routers_collection = db["routers"]

pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


class RegisterRequest(BaseModel):
    username: str
    password: str

    @validator("password")
    def password_strength(cls, v):
        if len(v) < 12:
            raise ValueError("Password must be at least 12 characters")
        return v

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserOut(BaseModel):
    id: str
    username: str

class RouterCreate(BaseModel):
    name: str
    ip: str
    username: str
    password: str

class RouterOut(BaseModel):
    id: str
    name: str
    ip: str


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    try:
        user_id = ObjectId(user_id_str)
    except Exception:
        raise credentials_exception

    user = await users_collection.find_one({"_id": user_id})
    if user is None:
        raise credentials_exception

    return user


# Public Auth Routes (no auth required)

@app.post("/register", response_model=UserOut, status_code=201)
async def register(data: RegisterRequest):
    if await users_collection.find_one({"username": data.username}):
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed = pwd_context.hash(data.password)
    result = await users_collection.insert_one({
        "username": data.username,
        "hashed_password": hashed,
        "created_at": datetime.utcnow()
    })

    logger.info(f"New user registered: {data.username}")
    return UserOut(id=str(result.inserted_id), username=data.username)

@app.post("/login", response_model=Token)
async def login(data: LoginRequest):
    user = await users_collection.find_one({"username": data.username})
    if not user or not pwd_context.verify(data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token({"sub": str(user["_id"])})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/me", response_model=UserOut)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return UserOut(
        id=str(current_user["_id"]),
        username=current_user["username"]
    )


# Protected Router Routes

protected_router = APIRouter(
    prefix="/routers",
    tags=["routers"],
    dependencies=[Depends(get_current_user)]  # All routes here require auth
)

@protected_router.post("/", response_model=RouterOut, status_code=201)
async def add_router(router_data: RouterCreate, current_user: dict = Depends(get_current_user)):
    new_router = {
        "name": router_data.name,
        "ip": router_data.ip,
        "username": router_data.username,
        "password": router_data.password,  # TODO: encrypt later
        "owner_id": str(current_user["_id"]),
        "created_at": datetime.utcnow()
    }

    result = await routers_collection.insert_one(new_router)
    return RouterOut(
        id=str(result.inserted_id),
        name=router_data.name,
        ip=router_data.ip
    )

@protected_router.get("/", response_model=List[RouterOut])
async def get_my_routers(current_user: dict = Depends(get_current_user)):
    cursor = routers_collection.find({"owner_id": str(current_user["_id"])})
    routers = []
    async for r in cursor:
        routers.append(RouterOut(
            id=str(r["_id"]),
            name=r["name"],
            ip=r["ip"]
        ))
    return routers

@protected_router.delete("/{router_id}")
async def delete_router(router_id: str, current_user: dict = Depends(get_current_user)):
    try:
        obj_id = ObjectId(router_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid router ID")

    result = await routers_collection.delete_one({
        "_id": obj_id,
        "owner_id": str(current_user["_id"])
    })

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Router not found")

    return {"message": "Router deleted"}

app.include_router(protected_router)
app.include_router(bridge.router)
app.include_router(system.router)
app.include_router(interfaces.router)
app.include_router(hotspot.router)
app.include_router(wan.router)
app.include_router(dhcp.router)

# Run

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

