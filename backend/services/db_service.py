# /Users/1byinf8/Documents/quant-api/services/db_service.py
import sqlite3
import os
from models.blockchain import Block, BlockData
from typing import List

DB_PATH = os.path.join(os.path.dirname(__file__), "../database/quant.db")

def init_db():
    """Initialize SQLite database with blocks table."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL,
            file_hash TEXT,
            key BLOB,
            key_hash TEXT,
            file_name TEXT,
            file_size INTEGER,
            owner TEXT,
            file_id TEXT UNIQUE,
            shared_with TEXT,
            prev_hash TEXT,
            nonce INTEGER,
            hash TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_block(block: Block) -> None:
    """Save a block to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO blocks (
            timestamp, file_hash, key, key_hash, file_name, file_size, owner, 
            file_id, shared_with, prev_hash, nonce, hash
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        block.timestamp, block.file_hash.hex(), block.key, block.key_hash, 
        block.file_name, block.file_size, block.owner, block.file_id, 
        ','.join(block.shared_with), block.prev_hash, block.nonce, block.hash
    ))
    conn.commit()
    conn.close()

def load_blockchain() -> List[Block]:
    """Load all blocks from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM blocks ORDER BY id")
    rows = cursor.fetchall()
    conn.close()
    
    blockchain = []
    for row in rows:
        block_data = BlockData(
            timestamp=row[1],
            file_hash=row[2],
            key_hash=row[4],
            file_name=row[5],
            file_size=row[6],
            owner=row[7],
            file_id=row[8],
            shared_with=row[9].split(','),
            prev_hash=row[10],
            nonce=row[11],
            hash=row[12]
        )
        block = Block.from_data(block_data, key=row[3])  # Pass key from DB
        blockchain.append(block)
    return blockchain

def get_block_by_file_id(file_id: str) -> Block:
    """Retrieve a block by file_id."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM blocks WHERE file_id = ?", (file_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    block_data = BlockData(
        timestamp=row[1],
        file_hash=row[2],
        key_hash=row[4],
        file_name=row[5],
        file_size=row[6],
        owner=row[7],
        file_id=row[8],
        shared_with=row[9].split(','),
        prev_hash=row[10],
        nonce=row[11],
        hash=row[12]
    )
    return Block.from_data(block_data, key=row[3])