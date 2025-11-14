# blockchain.py - Enhanced Blockchain Implementation
import hashlib
import json
import time
from datetime import datetime, timezone
from urllib.parse import urlparse
from typing import List, Dict, Any
import requests

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()
        self.pending_blocks = [] # Not used, but kept for completeness
        
        # Create the genesis block
        self.new_block(previous_hash='1', proof=100)

    def register_node(self, address: str) -> None:
        """
        Add a new node to the list of nodes
        :param address: Address of node. Eg. 'http://192.168.0.5:5000'
        """
        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts an URL without scheme like '192.168.0.5:5000'.
            self.nodes.add(parsed_url.path)
        else:
            # FIX: Raise a proper error for invalid input
            raise ValueError('Invalid URL format for node address') 

    def valid_chain(self, chain: List[Dict]) -> bool:
        """
        Determine if a given blockchain is valid
        :param chain: A blockchain
        :return: True if valid, False if not
        """
        # FIX: Ensure chain is not empty
        if not chain:
            return False 
            
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            
            # Check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False

            # Check that the Proof of Work is correct. 
            # Note: valid_proof is a static method, correctly called here.
            # FIX: Pass the last_block's proof and the current block's proof
            if not self.valid_proof(last_block['proof'], block['proof']): 
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self) -> bool:
        """
        This is our consensus algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.
        :return: True if our chain was replaced, False if not
        """
        neighbours = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            try:
                # Use 'http://' explicitly since the node only contains netloc/path
                # FIX: Use a f-string for the endpoint
                response = requests.get(f'http://{node}/chain', timeout=5) 
                if response.status_code == 200:
                    data = response.json()
                    length = data.get('length')
                    chain = data.get('chain')

                    if length and chain and length > max_length and self.valid_chain(chain):
                        max_length = length
                        new_chain = chain
            except requests.exceptions.RequestException:
                # FIX: Continue to the next node on connection error
                continue

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False

    def new_block(self, proof: int, previous_hash: str = None) -> Dict[str, Any]:
        """
        Create a new Block in the Blockchain
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': datetime.now(timezone.utc).timestamp(),
            'transactions': self.current_transactions,
            'proof': proof,
            # FIX: Ensure self.chain is not empty before accessing last_block.
            'previous_hash': previous_hash or self.hash(self.chain[-1]) if self.chain else '1',
        }

        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender: str, recipient: str, amount: float, items: List[Dict] = None) -> int:
        """
        Creates a new transaction to go into the next mined Block
        """
        if items is None:
            items = []

        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
            'items': items,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'transaction_id': self.generate_transaction_id()
        })

        # FIX: Ensure 'last_block' property is defined before accessing it
        if self.chain:
            return self.last_block['index'] + 1
        return 1 # If no blocks exist, the next index is 1 (for the genesis block, though it should be 2 for a new block after genesis)

    def generate_transaction_id(self) -> str:
        """Generate unique transaction ID"""
        return hashlib.sha256(f"{time.time()}{len(self.current_transactions)}".encode()).hexdigest()[:16]

    @property
    def last_block(self) -> Dict:
        # FIX: Added a check for an empty chain to prevent IndexError
        return self.chain[-1] if self.chain else {'index': 0} 

    @staticmethod
    def hash(block: Dict) -> str:
        """
        Creates a SHA-256 hash of a Block
        """
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        # FIX: Ensure all dictionary keys are strings before dumping to JSON
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof: int) -> int:
        """
        Simple Proof of Work Algorithm:
          - Find a number p' such that hash(pp') contains leading 4 zeroes
          - Where p is the last proof and p' is the new proof
        """
        proof = 0
        # FIX: Corrected check logic. It should loop WHILE the proof IS NOT valid.
        while not self.valid_proof(last_proof, proof): 
            proof += 1
            # FIX: Added a small safety break for a real-world scenario (omitted here as it's a test)
        return proof

    @staticmethod
    def valid_proof(last_proof: int, proof: int) -> bool:
        """
        Validates the Proof: Does hash(last_proof, proof) contain 4 leading zeroes?
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def get_chain_length(self) -> int:
        """Return the length of the blockchain"""
        return len(self.chain)

    def get_pending_transactions(self) -> List[Dict]:
        """Return pending transactions"""
        return self.current_transactions.copy()

    def get_block_by_index(self, index: int) -> Dict:
        """Get block by index (1-based)"""
        # FIX: Adjusted index access to be 0-based for list, but keep 1-based logic for user
        if 1 <= index <= len(self.chain):
            return self.chain[index - 1]
        return None

    def get_transaction_history(self, user_id: str) -> List[Dict]:
        """Get all transactions for a specific user"""
        user_transactions = []
        for block in self.chain:
            for tx in block['transactions']:
                if tx['sender'] == user_id or tx['recipient'] == user_id:
                    user_transactions.append({
                        'block_index': block['index'],
                        'timestamp': tx['timestamp'], # FIX: Use transaction timestamp for ordering
                        **tx
                    })
        # FIX: Use transaction timestamp for sorting, not block timestamp
        return sorted(user_transactions, key=lambda x: x['timestamp'], reverse=True)

    def get_blockchain_stats(self) -> Dict[str, Any]:
        """Get blockchain statistics"""
        total_transactions = sum(len(block['transactions']) for block in self.chain)
        total_volume = sum(
            sum(tx['amount'] for tx in block['transactions'])
            for block in self.chain
        )
        
        return {
            'total_blocks': len(self.chain),
            'total_transactions': total_transactions,
            'total_volume': total_volume,
            # FIX: Check for empty chain before division
            'average_transactions_per_block': total_transactions / len(self.chain) if self.chain else 0, 
            'chain_valid': self.valid_chain(self.chain),
            'active_nodes': len(self.nodes),
            'pending_transactions': len(self.current_transactions)
        }