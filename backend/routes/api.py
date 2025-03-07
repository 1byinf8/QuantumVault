# /Users/1byinf8/Documents/quant-api/routes/api.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import socketio
from services.file_service import upload_file, download_file, register_user,check_email, login_user
from models.blockchain import main_blockchain
from dataclasses import asdict

router = APIRouter()
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='http://localhost:3000')

@router.post("/register")
async def register_user_endpoint(username: str):
    print(username)
class SignupRequest(BaseModel):
    username: str  # Changed from FE's 'name' to match BE
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/signup")
async def register_user_endpoint(request: SignupRequest):
    print(request.username)
    try:
        return await register_user(request.username, request.email, request.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/check-email")
async def check_email_endpoint(email: str):
    try:    
        return await check_email(email)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login_user_endpoint(request: LoginRequest):
    try:
        return await login_user(request.email, request.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/upload")
async def upload_file_endpoint(file: UploadFile = File(...), shared_with: str = "bob", owner: str = "alice"):
    print(file)
    try:
        return await upload_file(file, shared_with, owner, sio)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.get("/download/{file_id}")
async def download_file_endpoint(file_id: str, user_id: str = "bob"):
    try:
        decrypted_path, filename = download_file(file_id, user_id)
        return FileResponse(decrypted_path, filename=filename)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.get("/blockchain")
async def get_blockchain():
    return [asdict(block.to_data()) for block in main_blockchain]

@sio.event
async def connect(sid, environ):
    print(f"Client {sid} connected")
    await sio.emit('blockchain_update', [asdict(block.to_data()) for block in main_blockchain], room=sid)

@sio.event
async def disconnect(sid):
    print(f"Client {sid} disconnected")