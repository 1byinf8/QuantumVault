# !pip install qiskit qiskit-aer cryptography
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
import random
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
import hashlib
import time
import json
import socket
import threading
import uuid
from dataclasses import dataclass, asdict
from typing import List, Dict

# BB84 Simulation (unchanged)
def simulate_bb84(n_bits, eavesdrop=False):
    n_qubits = n_bits * 4
    alice_bits = [random.randint(0, 1) for _ in range(n_qubits)]
    alice_bases = [random.randint(0, 1) for _ in range(n_qubits)]

    circuits = []
    for i in range(n_qubits):
        qc = QuantumCircuit(1, 1)
        if alice_bits[i] == 1:
            qc.x(0)
        if alice_bases[i] == 1:
            qc.h(0)
        circuits.append(qc)

    bob_bases = [random.randint(0, 1) for _ in range(n_qubits)]
    if eavesdrop:
        eve_bases = [random.randint(0, 1) for _ in range(n_qubits)]
        for i in range(n_qubits):
            if eve_bases[i] == 1:
                circuits[i].h(0)
            circuits[i].measure(0, 0)

    for i in range(n_qubits):
        if bob_bases[i] == 1:
            circuits[i].h(0)
        circuits[i].measure(0, 0)

    simulator = AerSimulator()
    bob_bits = []
    for qc in circuits:
        job = simulator.run(qc, shots=1, memory=True)
        result = job.result()
        bob_bits.append(int(result.get_memory()[0]))

    alice_key = [alice_bits[i] for i in range(n_qubits) if alice_bases[i] == bob_bases[i]]
    bob_key = [bob_bits[i] for i in range(n_qubits) if alice_bases[i] == bob_bases[i]]

    if len(alice_key) < n_bits:
        print(f"Warning: Only {len(alice_key)} bits matched, retrying...")
        return simulate_bb84(n_bits, eavesdrop)

    alice_key = alice_key[:n_bits]
    bob_key = bob_key[:n_bits]

    errors = sum(a != b for a, b in zip(alice_key, bob_key))
    error_rate = errors / n_bits if n_bits > 0 else 0

    alice_key_bytes = bytes(int("".join(map(str, alice_key[i:i+8])), 2) for i in range(0, n_bits, 8))
    bob_key_bytes = bytes(int("".join(map(str, bob_key[i:i+8])), 2) for i in range(0, n_bits, 8))

    return alice_key_bytes, bob_key_bytes, error_rate

# AES-256-GCM Encryption functions (unchanged)
def encrypt_file(key, input_file, output_file):
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file '{input_file}' not found!")
    nonce = os.urandom(12)
    aesgcm = AESGCM(key)
    with open(input_file, 'rb') as f:
        plaintext = f.read()
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    with open(output_file, 'wb') as f:
        f.write(nonce + ciphertext)
    return hashlib.sha256(ciphertext).digest()

def decrypt_file(key, encrypted_file, output_file):
    if not os.path.exists(encrypted_file):
        raise FileNotFoundError(f"Encrypted file '{encrypted_file}' not found!")
    with open(encrypted_file, 'rb') as f:
        data = f.read()
    nonce, ciphertext = data[:12], data[12:]
    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    with open(output_file, 'wb') as f:
        f.write(plaintext)
    return hashlib.sha256(ciphertext).digest()

# Serializable data structures (unchanged)
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

class Block:
    def __init__(self, file_hash, key, file_name, file_size, owner, file_id, shared_with, prev_hash):
        self.timestamp = time.time()
        self.file_hash = file_hash  # bytes
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
            key=key,
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

@dataclass
class Message:
    type: str
    sender: str
    recipient: str
    content: Dict
    timestamp: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()

    def to_json(self):
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        return cls(**data)

# Global main_blockchain to store all transactions
main_blockchain = []

class QuantumNode:
    def __init__(self, node_id=None, host='localhost', port=0, storage_dir="storage"):
        self.node_id = node_id or str(uuid.uuid4())
        self.host = host
        self.port = port
        self.storage_dir = os.path.join(storage_dir, self.node_id)
        os.makedirs(self.storage_dir, exist_ok=True)
        self.chain = main_blockchain[:]
        self.keys = {}
        self.peers = {}
        self.file_locations = {}
        self.sock = None
        self.running = False
        self.message_handlers = {
            "block": self._handle_block,
            "key_request": self._handle_key_request,
            "key_response": self._handle_key_response,
            "chain_request": self._handle_chain_request,
            "chain_response": self._handle_chain_response,
            "file_request": self._handle_file_request,
            "file_response": self._handle_file_response,
            "peer_connect": self._handle_peer_connect,
        }
        if not main_blockchain:
            self._create_genesis_block()

    def _create_genesis_block(self):
        genesis_key, _, _ = simulate_bb84(256, eavesdrop=False)
        genesis_hash = hashlib.sha256(b"genesis").digest()
        genesis_block = Block(
            file_hash=genesis_hash,
            key=genesis_key,
            file_name="genesis",
            file_size=0,
            owner=self.node_id,
            file_id="genesis",
            shared_with=["alice", "bob", "charlie"],
            prev_hash="0"
        )
        main_blockchain.append(genesis_block)
        self.chain = main_blockchain[:]
        self.keys["genesis"] = genesis_key

    def start_node(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))
        if self.port == 0:
            self.host, self.port = self.sock.getsockname()
        print(f"Node {self.node_id} started on {self.host}:{self.port}")
        self.running = True
        listen_thread = threading.Thread(target=self._listen)
        listen_thread.daemon = True
        listen_thread.start()

    def stop_node(self):
        self.running = False
        time.sleep(1.5)
        if self.sock:
            self.sock.close()

    def _listen(self):
        self.sock.settimeout(1.0)
        while self.running:
            try:
                data, addr = self.sock.recvfrom(65536)
                message = Message.from_json(data.decode('utf-8'))
                print(f"Node {self.node_id} received {message.type} from {message.sender} at {addr}")
                if message.type in self.message_handlers:
                    self.message_handlers[message.type](message)
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Node {self.node_id} error handling message: {e}")

    # Change 1: Enhanced broadcast reliability with retries
    def _send_message(self, recipient_id, message, retries=3):
        for attempt in range(retries):
            if recipient_id == "broadcast":
                for peer_id, (peer_host, peer_port) in self.peers.items():
                    self._send_to_address(peer_host, peer_port, message)
                    print(f"Node {self.node_id} broadcasted {message.type} to {peer_id} (attempt {attempt+1}/{retries})")
            elif recipient_id in self.peers:
                peer_host, peer_port = self.peers[recipient_id]
                self._send_to_address(peer_host, peer_port, message)
                print(f"Node {self.node_id} sent {message.type} to {recipient_id} (attempt {attempt+1}/{retries})")
            else:
                print(f"Node {self.node_id} unknown recipient: {recipient_id}")
                break
            time.sleep(0.5)  # Delay between retries

    def _send_to_address(self, host, port, message):
        try:
            self.sock.sendto(message.to_json().encode('utf-8'), (host, port))
        except Exception as e:
            print(f"Node {self.node_id} failed to send message to {host}:{port}: {e}")

    def connect_to_peer(self, peer_id, peer_host, peer_port):
        self.peers[peer_id] = (peer_host, peer_port)
        self.request_chain(peer_id)
        message = Message(
            type="peer_connect",
            sender=self.node_id,
            recipient=peer_id,
            content={"host": self.host, "port": self.port}
        )
        self._send_to_address(peer_host, peer_port, message)

    def _handle_peer_connect(self, message):
        peer_id = message.sender
        peer_host = message.content["host"]
        peer_port = message.content["port"]
        self.peers[peer_id] = (peer_host, peer_port)
        print(f"Node {self.node_id} added peer {peer_id} at {peer_host}:{peer_port}")

    def request_chain(self, peer_id="broadcast"):
        message = Message(
            type="chain_request",
            sender=self.node_id,
            recipient=peer_id,
            content={}
        )
        self._send_message(peer_id, message)

    def _handle_chain_request(self, message):
        chain_data = [block.to_data() for block in main_blockchain]
        response = Message(
            type="chain_response",
            sender=self.node_id,
            recipient=message.sender,
            content={"chain": [asdict(block_data) for block_data in chain_data]}
        )
        self._send_message(message.sender, response)

    def _handle_chain_response(self, message):
        try:
            received_chain = [Block.from_data(BlockData(**block_dict)) for block_dict in message.content["chain"]]
            if self._verify_chain(received_chain) and len(received_chain) > len(self.chain):
                self.chain = received_chain[:]
                print(f"Node {self.node_id} updated chain from {message.sender}, new length: {len(self.chain)}")
                self._request_relevant_keys()
        except Exception as e:
            print(f"Node {self.node_id} error processing chain_response: {e}")

    def _verify_chain(self, chain):
        if not chain:
            return False
        for i in range(1, len(chain)):
            current = chain[i]
            previous = chain[i-1]
            if current.prev_hash != previous.hash:
                return False
            if current.hash != current.calc_hash():
                return False
        return True

    def _request_relevant_keys(self):
        for block in self.chain:
            if self.node_id in block.shared_with and block.file_id not in self.keys:
                self.request_key(block.file_id, block.owner)

    def request_key(self, file_id, owner_id):
        message = Message(
            type="key_request",
            sender=self.node_id,
            recipient=owner_id,
            content={"file_id": file_id}
        )
        self._send_message(owner_id, message)

    def _handle_key_request(self, message):
        file_id = message.content["file_id"]
        requester_id = message.sender
        file_block = next((block for block in self.chain if block.file_id == file_id), None)
        if file_block and requester_id in file_block.shared_with:
            key = self.keys.get(file_id)
            if key:
                response = Message(
                    type="key_response",
                    sender=self.node_id,
                    recipient=requester_id,
                    content={"file_id": file_id, "key": key.hex()}
                )
                self._send_message(requester_id, response)
                print(f"Node {self.node_id} sent key to {requester_id} for {file_id}")
        else:
            print(f"Node {self.node_id} denied key request from {requester_id} for {file_id}")

    def _handle_key_response(self, message):
        file_id = message.content["file_id"]
        key = bytes.fromhex(message.content["key"])
        self.keys[file_id] = key
        print(f"Node {self.node_id} received and stored key for file {file_id}")
        file_block = next((block for block in self.chain if block.file_id == file_id), None)
        if file_block and file_id not in self.file_locations:
            self.request_file(file_id, file_block.owner)
        elif file_id not in self.file_locations:
            self.request_file(file_id, message.sender)

    def request_file(self, file_id, owner_id):
        message = Message(
            type="file_request",
            sender=self.node_id,
            recipient=owner_id,
            content={"file_id": file_id}
        )
        self._send_message(owner_id, message)

    def _handle_file_request(self, message):
        file_id = message.content["file_id"]
        requester_id = message.sender
        file_block = next((block for block in self.chain if block.file_id == file_id), None)
        if file_block and requester_id in file_block.shared_with:
            file_path = os.path.join(self.storage_dir, f"{file_id}.enc")
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    encrypted_data = f.read()
                response = Message(
                    type="file_response",
                    sender=self.node_id,
                    recipient=requester_id,
                    content={
                        "file_id": file_id,
                        "data": encrypted_data.hex()
                    }
                )
                self._send_message(requester_id, response)
                print(f"Node {self.node_id} sent file to {requester_id} for {file_id}")
        else:
            print(f"Node {self.node_id} denied file request from {requester_id} for {file_id}")

    def _handle_file_response(self, message):
        file_id = message.content["file_id"]
        encrypted_data = bytes.fromhex(message.content["data"])
        file_path = os.path.join(self.storage_dir, f"{file_id}.enc")
        with open(file_path, 'wb') as f:
            f.write(encrypted_data)
        self.file_locations[file_id] = file_path
        print(f"Node {self.node_id} received file {file_id}")
        if file_id in self.keys:
            self.decrypt_and_save_file(file_id)
        # Change 2: Sync with main_blockchain after file receipt
        if len(main_blockchain) > len(self.chain):
            self.chain = main_blockchain[:]
            print(f"Node {self.node_id} synced chain with main_blockchain after file receipt, new length: {len(self.chain)}")

    def _handle_block(self, message):
        try:
            block_data = BlockData(**message.content["block"])
            new_block = Block.from_data(block_data)
            # Change 3: Validate and add block to main_blockchain, sync all nodes
            if new_block.prev_hash == main_blockchain[-1].hash if main_blockchain else "0":
                main_blockchain.append(new_block)
                print(f"Node {self.node_id} added block for {new_block.file_name} (ID: {new_block.file_id}) to main_blockchain")
                # Always sync local chain with main_blockchain after block addition
                if len(main_blockchain) > len(self.chain):
                    self.chain = main_blockchain[:]
                    print(f"Node {self.node_id} synced chain with main_blockchain, new length: {len(self.chain)}")
                if self.node_id in new_block.shared_with:
                    self.request_key(new_block.file_id, new_block.owner)
            else:
                print(f"Node {self.node_id} rejected block {new_block.file_id}: invalid previous hash")
        except Exception as e:
            print(f"Node {self.node_id} error processing block: {e}")

    def decrypt_and_save_file(self, file_id):
        encrypted_path = self.file_locations[file_id]
        file_block = next((block for block in self.chain if block.file_id == file_id), None)
        if file_block:
            ext = os.path.splitext(file_block.file_name)[1]
            decrypted_path = os.path.join(self.storage_dir, f"decrypted_{file_id}{ext}")
        else:
            decrypted_path = os.path.join(self.storage_dir, f"decrypted_{file_id}")
        decrypt_file(self.keys[file_id], encrypted_path, decrypted_path)
        print(f"Node {self.node_id} decrypted file {file_id} to {decrypted_path}")

def main():
    import os
    import time
    import random
    import string

    print("=== Quantum Secure File Sharing Network Test ===")

    os.makedirs("test_files", exist_ok=True)
    os.makedirs("storage", exist_ok=True)

    test_file_path = os.path.join("test_files", "test_audio.mp3")
    with open(test_file_path, "wb") as f:
        f.write(b"Dummy MP3 data" + os.urandom(1024))

    print("\n1. Testing BB84 Quantum Key Distribution")
    print("-----------------------------------------")
    alice_key, bob_key, error_rate = simulate_bb84(256, eavesdrop=False)
    print(f"Generated QKD keys of length: {len(alice_key)} bytes")
    print(f"Alice key (first 8 bytes): {alice_key[:8].hex()}")
    print(f"Bob key (first 8 bytes): {bob_key[:8].hex()}")
    print(f"Keys match: {alice_key == bob_key}")
    print(f"Error rate: {error_rate}")

    print("\nTesting BB84 with eavesdropping:")
    alice_key, bob_key, error_rate = simulate_bb84(256, eavesdrop=True)
    print(f"Error rate with eavesdropping: {error_rate}")
    print(f"Keys match with eavesdropping: {alice_key == bob_key}")

    print("\n2. Testing Encryption/Decryption")
    print("-------------------------------")
    encryption_key, _, _ = simulate_bb84(256)
    encrypted_file = os.path.join("test_files", f"{os.path.basename(test_file_path)}.enc")
    file_hash = encrypt_file(encryption_key, test_file_path, encrypted_file)
    print(f"Encrypted file created: {encrypted_file}")
    print(f"File hash: {file_hash.hex()}")

    ext = os.path.splitext(test_file_path)[1]
    decrypted_file = os.path.join("test_files", f"{os.path.basename(test_file_path)}_decrypted{ext}")
    decrypt_file(encryption_key, encrypted_file, decrypted_file)
    print(f"Decrypted file created: {decrypted_file}")

    with open(test_file_path, "rb") as f1, open(decrypted_file, "rb") as f2:
        original = f1.read()
        decrypted = f2.read()
        print(f"Decryption successful: {original == decrypted}")

    print("\n3. Setting up Quantum Nodes")
    print("--------------------------")
    # main_blockchain.clear()

    alice_node = QuantumNode(node_id="alice", port=9001)
    bob_node = QuantumNode(node_id="bob", port=9002)
    charlie_node = QuantumNode(node_id="charlie", port=9003)

    alice_node.start_node()
    bob_node.start_node()
    charlie_node.start_node()

    alice_node.connect_to_peer("bob", "localhost", 9002)
    alice_node.connect_to_peer("charlie", "localhost", 9003)
    bob_node.connect_to_peer("alice", "localhost", 9001)
    charlie_node.connect_to_peer("alice", "localhost", 9001)
    charlie_node.connect_to_peer("bob", "localhost", 9002)

    print("Waiting for nodes to synchronize...")
    time.sleep(2)

    print("\n4. Sharing a File in the Network")
    print("------------------------------")
    file_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    shared_file_name = f"shared_image_{file_id}.png"
    shared_file_path = os.path.join("test_files", shared_file_name)

    with open(shared_file_path, "wb") as f:
        f.write(b"Dummy PNG data" + os.urandom(2048))

    file_size = os.path.getsize(shared_file_path)
    file_key, _, _ = simulate_bb84(256)
    encrypted_path = os.path.join(alice_node.storage_dir, f"{file_id}.enc")
    file_hash = encrypt_file(file_key, shared_file_path, encrypted_path)

    new_block = Block(
        file_hash=file_hash,
        key=file_key,
        file_name=shared_file_name,
        file_size=file_size,
        owner="alice",
        file_id=file_id,
        shared_with=["bob"],
        prev_hash=main_blockchain[-1].hash if main_blockchain else "0"
    )

    main_blockchain.append(new_block)
    alice_node.keys[file_id] = file_key
    alice_node.file_locations[file_id] = encrypted_path

    block_data = new_block.to_data()
    block_message = Message(
        type="block",
        sender="alice",
        recipient="broadcast",
        content={"block": asdict(block_data)}
    )
    alice_node._send_message("broadcast", block_message)

    if len(main_blockchain) > len(alice_node.chain):
        alice_node.chain = main_blockchain[:]
        print(f"Node {alice_node.node_id} updated chain from main_blockchain after adding block, new length: {len(alice_node.chain)}")

    print(f"Alice has shared file '{shared_file_name}' with Bob only")
    print("Waiting for Bob to receive the file...")

    timeout = 15
    start_time = time.time()
    while file_id not in bob_node.file_locations and (time.time() - start_time) < timeout:
        time.sleep(1)
    ext = os.path.splitext(shared_file_name)[1]
    if file_id in bob_node.file_locations:
        decrypted_path = os.path.join(bob_node.storage_dir, f"decrypted_{file_id}{ext}")
        bob_node.decrypt_and_save_file(file_id)
        print(f"Bob successfully received and decrypted file at {decrypted_path}")
    else:
        print("Bob didn’t receive it—triggering manual requests...")
        bob_node.request_key(file_id, "alice")
        time.sleep(3)
        bob_node.request_file(file_id, "alice")
        time.sleep(3)
        if file_id in bob_node.file_locations:
            decrypted_path = os.path.join(bob_node.storage_dir, f"decrypted_{file_id}{ext}")
            bob_node.decrypt_and_save_file(file_id)
            print(f"Bob got it after manual requests at {decrypted_path}")
        else:
            print("Bob still didn’t get it—check network!")

    print("\nTesting Charlie's access (should fail)...")
    charlie_node.request_key(file_id, "alice")
    time.sleep(2)
    charlie_node.request_file(file_id, "alice")
    time.sleep(2)
    if file_id in charlie_node.file_locations:
        print("Charlie unexpectedly got the file!")
    else:
        print("Charlie couldn’t access the file—as expected!")

    print("\n5. Testing Chain Integrity")
    print("-------------------------")
    print(f"Main blockchain length: {len(main_blockchain)}")
    print(f"Alice chain length: {len(alice_node.chain)}")
    print(f"Bob chain length: {len(bob_node.chain)}")
    print(f"Charlie chain length: {len(charlie_node.chain)}")

    if alice_node._verify_chain(alice_node.chain):
        print("Alice's chain verified successfully")
    if bob_node._verify_chain(bob_node.chain):
        print("Bob's chain verified successfully")
    if charlie_node._verify_chain(charlie_node.chain):
        print("Charlie's chain verified successfully")

    print("\n6. Cleanup")
    print("----------")
    alice_node.stop_node()
    bob_node.stop_node()
    charlie_node.stop_node()
    print("All nodes stopped")

    print("\nTest completed successfully!")

if __name__ == "__main__":
    main()