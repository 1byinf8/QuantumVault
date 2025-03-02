# /Users/1byinf8/Documents/quant-api/services/file_service.py
import os
import uuid
from models.blockchain import Block, main_blockchain, users
from utils.quantum import simulate_bb84
from utils.encryption import encrypt_file, decrypt_file
from dataclasses import asdict

async def register_user(username: str) -> dict:
    if any(user.username == username for user in users):
        raise ValueError(f"Username '{username}' already exists")
    users.append(username)
    return {"username": username, "status": "User registered successfully"}

async def check_email(email: str) -> dict:
    """Check if an email is already registered."""
    exists = any(user.email == email for user in users)
    return {"email": email, "exists": exists}

async def upload_file(file, shared_with: str, owner: str, sio):
    # Validate owner and shared_with users
    if owner not in users:
        raise ValueError(f"Owner '{owner}' is not a registered user")
    shared_with_list = shared_with.split(",")
    for user in shared_with_list:
        if user not in users:
            raise ValueError(f"User '{user}' in shared_with is not registered")

    file_id = str(uuid.uuid4())
    file_path = os.path.join("storage", f"{file_id}_{file.filename}")
    encrypted_path = os.path.join("storage", f"{file_id}.enc")
    
    os.makedirs("storage", exist_ok=True)
    
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    file_key, _, _ = simulate_bb84(256)
    file_hash = encrypt_file(file_key, file_path, encrypted_path)
    
    new_block = Block(
        file_hash=file_hash,
        key=file_key,
        file_name=file.filename,
        file_size=os.path.getsize(file_path),
        owner=owner,
        file_id=file_id,
        shared_with=shared_with_list,
        prev_hash=main_blockchain[-1].hash if main_blockchain else "0"
    )
    
    main_blockchain.append(new_block)
    await sio.emit('new_block', asdict(new_block.to_data()))
    
    return {"file_id": file_id, "status": "File uploaded and encrypted"}

def download_file(file_id: str, user_id: str):
    file_block = next((block for block in main_blockchain if block.file_id == file_id), None)
    if not file_block or user_id not in file_block.shared_with:
        raise ValueError("File not found or access denied")
    
    encrypted_path = os.path.join("storage", f"{file_block.file_id}.enc")
    decrypted_path = os.path.join("storage", f"decrypted_{file_block.file_id}{os.path.splitext(file_block.file_name)[1]}")
    decrypt_file(file_block.key, encrypted_path, decrypted_path)
    
    return decrypted_path, file_block.file_name