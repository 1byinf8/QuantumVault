from dataclasses import dataclass, asdict
import hashlib
import time
import json
import atexit
import os
from typing import List

@dataclass
class BlockData:
    timestamp: float
    file_hash: str
    key_hash: str
    file_name: str
    file_size: int
    owner: str
    file_id: str
    shared_with: List[str]
    prev_hash: str
    nonce: int = 0
    hash: str = ""

@dataclass
class User:
    username: str
    email: str

class Block:
    def __init__(self, file_hash, key, file_name, file_size, owner, file_id, shared_with, prev_hash):
        self.timestamp = time.time()
        self.file_hash = file_hash
        self.key = key
        self.key_hash = hashlib.sha256(key).hexdigest()
        self.file_name = file_name
        self.file_size = file_size
        self.owner = owner
        self.file_id = file_id
        self.shared_with = shared_with
        self.prev_hash = prev_hash
        self.nonce = 0
        self.hash = self.calc_hash()

    def calc_hash(self):
        block_str = (f"{self.timestamp}{self.file_hash.hex()}{self.key_hash}"
                     f"{self.file_name}{self.file_size}{self.owner}{self.file_id}"
                     f"{','.join(self.shared_with)}{self.prev_hash}{self.nonce}")
        return hashlib.sha256(block_str.encode()).hexdigest()

    def to_data(self) -> BlockData:
        return BlockData(
            timestamp=self.timestamp,
            file_hash=self.file_hash.hex(),
            key_hash=self.key_hash,
            file_name=self.file_name,
            file_size=self.file_size,
            owner=self.owner,
            file_id=self.file_id,
            shared_with=self.shared_with,
            prev_hash=self.prev_hash,
            nonce=self.nonce,
            hash=self.hash
        )

    @classmethod
    def from_data(cls, data: BlockData, key=None):
        block = cls(
            file_hash=bytes.fromhex(data.file_hash),
            key=key or bytes.fromhex(data.key_hash),
            file_name=data.file_name,
            file_size=data.file_size,
            owner=data.owner,
            file_id=data.file_id,
            shared_with=data.shared_with,
            prev_hash=data.prev_hash
        )
        block.timestamp = data.timestamp
        block.nonce = data.nonce
        block.hash = data.hash
        block.key_hash = data.key_hash
        return block

# Global in-memory storage
main_blockchain: List[Block] = []
users: List[User] = []  # Store registered users

# File path for persistent storage
DATA_FILE = "blockchain_data.json"

def save_blockchain_to_json():
    """
    Saves the blockchain and user data to a JSON file.
    This function will be called automatically when the application exits.
    """
    global main_blockchain, users
    
    # Create the data structure to save
    data = {
        "blockchain": [block.to_data().__dict__ for block in main_blockchain],
        "users": [asdict(user) for user in users]
    }
    
    # Write to JSON file
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Blockchain data saved to {DATA_FILE}")

def initialize_blockchain():
    load_blockchain_from_json()

def load_blockchain_from_json():

    global main_blockchain, users
    
    if not os.path.exists(DATA_FILE):
        print(f"No existing blockchain data found at {DATA_FILE}")
        return
    
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
        
        # Restore blockchain
        main_blockchain = []
        for block_data in data.get("blockchain", []):
            # Convert dictionary back to BlockData
            block_data_obj = BlockData(**block_data)
            # Create Block from BlockData
            block = Block.from_data(block_data_obj)
            main_blockchain.append(block)
        
        # Restore users
        users = []
        for user_data in data.get("users", []):
            user = User(**user_data)
            users.append(user)
        
        print(f"Loaded {len(main_blockchain)} blocks and {len(users)} users from {DATA_FILE}")
    except Exception as e:
        print(f"Error loading blockchain data: {e}")

# Register the save function to run when the program exits
atexit.register(save_blockchain_to_json)

