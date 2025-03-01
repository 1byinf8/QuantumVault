from hashlib import sha3_256
import random
import time
from qiskit import QuantumCircuit, Aer, execute

# BB84 Quantum Key Distribution Simulation
def bb84_simulation(bit_length=16):
    qc = QuantumCircuit(1, 1)
    key = ""
    for i in range(bit_length):
        qc.h(0)
        qc.measure(0, 0)
        simulator = Aer.get_backend('qasm_simulator')
        result = execute(qc, simulator, shots=1).result()
        key += list(result.get_counts().keys())[0]
    return key

# SHA-3 Hash Function for Quantum Resistance
def sha3_hash(data):
    return sha3_256(data.encode()).hexdigest()

class Wallet:
    def __init__(self, owner):
        self.owner = owner
        self.balance = 100  # Default starting balance
        self.public_key = bb84_simulation(32)  # Simulated quantum key
        self.transaction_history = []  # Track transactions for validation
    
    def transfer(self, receiver, amount):
        if self.balance >= amount and amount > 0:
            # Only update balances, actual transfer happens when mined
            transaction = {
                "sender": self.owner,
                "sender_key": self.public_key,
                "receiver": receiver.owner,
                "receiver_key": receiver.public_key,
                "amount": amount,
                "timestamp": time.time()
            }
            return transaction
        else:
            return None

class Block:
    def __init__(self, index, previous_hash, transactions, quantum_key, difficulty=2):
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.quantum_key = quantum_key
        self.difficulty = difficulty
        self.nonce = 0
        self.hash = self.mine_block()
    
    def calculate_hash(self):
        data = f"{self.index}{self.timestamp}{self.transactions}{self.previous_hash}{self.quantum_key}{self.nonce}"
        return sha3_hash(data)
    
    def mine_block(self):
        # Simple proof-of-work: find a hash with 'difficulty' leading zeros
        target = '0' * self.difficulty
        while True:
            self.hash = self.calculate_hash()
            if self.hash.startswith(target):
                print(f"Block #{self.index} mined! Nonce: {self.nonce}, Hash: {self.hash}")
                return self.hash
            self.nonce += 1

class QuantumBlockchain:
    def __init__(self, difficulty=2):
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []
        self.difficulty = difficulty
        self.wallets = {}  # Store wallets for validation
    
    def create_genesis_block(self):
        return Block(0, "0", ["Genesis Block"], bb84_simulation(), self.difficulty)
    
    def register_wallet(self, wallet):
        # Register wallet for validation purposes
        self.wallets[wallet.owner] = wallet
    
    def validate_transaction(self, transaction):
        if not isinstance(transaction, dict):
            print("Invalid transaction format")
            return False
            
        # Check if transaction has all required fields
        required_fields = ["sender", "sender_key", "receiver", "receiver_key", "amount", "timestamp"]
        if not all(field in transaction for field in required_fields):
            print("Transaction missing required fields")
            return False
            
        # Check if sender and receiver exist
        if transaction["sender"] not in self.wallets or transaction["receiver"] not in self.wallets:
            print("Unknown sender or receiver")
            return False
            
        # Verify sender has sufficient balance
        sender_wallet = self.wallets[transaction["sender"]]
        if sender_wallet.balance < transaction["amount"]:
            print("Insufficient balance")
            return False
            
        # Verify amount is positive
        if transaction["amount"] <= 0:
            print("Invalid amount")
            return False
            
        # Verify public keys match
        if sender_wallet.public_key != transaction["sender_key"]:
            print("Sender key mismatch")
            return False
            
        return True
    
    def add_transaction(self, sender, receiver, amount):
        # Create the transaction
        transaction = sender.transfer(receiver, amount)
        
        # Validate the transaction before adding to pending
        if transaction and self.validate_transaction(transaction):
            self.pending_transactions.append(transaction)
            print(f"Transaction from {sender.owner} to {receiver.owner} for {amount} Q-Coins validated and pending")
            return True
        else:
            print("Transaction failed validation")
            return False
    
    def mine_block(self):
        if not self.pending_transactions:
            print("No pending transactions to mine")
            return False
            
        previous_block = self.chain[-1]
        quantum_key = bb84_simulation()
        
        print(f"Mining block with {len(self.pending_transactions)} transactions...")
        new_block = Block(
            len(self.chain), 
            previous_block.hash, 
            self.pending_transactions, 
            quantum_key,
            self.difficulty
        )
        
        # Add the block to the chain
        self.chain.append(new_block)
        
        # Process transactions (update balances) now that they're confirmed
        for transaction in self.pending_transactions:
            sender = self.wallets[transaction["sender"]]
            receiver = self.wallets[transaction["receiver"]]
            amount = transaction["amount"]
            
            sender.balance -= amount
            receiver.balance += amount
            
            # Record in transaction history
            sender.transaction_history.append(f"Sent {amount} Q-Coins to {receiver.owner}")
            receiver.transaction_history.append(f"Received {amount} Q-Coins from {sender.owner}")
        
        # Clear pending transactions
        self.pending_transactions = []
        return True
    
    def display_chain(self):
        for block in self.chain:
            print(f"Index: {block.index}")
            print(f"Hash: {block.hash}")
            print(f"Previous: {block.previous_hash}")
            print(f"Nonce: {block.nonce}")
            print(f"Difficulty: {block.difficulty}")
            print(f"Transactions: {block.transactions}")
            print(f"Quantum Key: {block.quantum_key}")
            print(f"{'-'*40}")

# Example usage
if __name__ == "__main__":
    # Create Wallets
    alice = Wallet("Alice")
    bob = Wallet("Bob")
    charlie = Wallet("Charlie")
    
    # Initialize Quantum Blockchain with difficulty 2 (two leading zeros)
    qblockchain = QuantumBlockchain(difficulty=2)
    
    # Register wallets
    qblockchain.register_wallet(alice)
    qblockchain.register_wallet(bob)
    qblockchain.register_wallet(charlie)
    
    # Alice sends 5 Q-Coins to Bob
    qblockchain.add_transaction(alice, bob, 5)
    
    # Bob sends 2 Q-Coins to Charlie
    qblockchain.add_transaction(bob, charlie, 2)
    
    # Mine the block to confirm transactions
    qblockchain.mine_block()
    
    # Display blockchain and balances
    qblockchain.display_chain()
    print(f"Alice's Balance: {alice.balance}")
    print(f"Bob's Balance: {bob.balance}")
    print(f"Charlie's Balance: {charlie.balance}")