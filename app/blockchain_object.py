import hashlib
import json
import requests
from time import time
from urllib.parse import urlparse


class Blockchain:
    def __init__(self):
        self.chain = [{
            "index": 1,
            "timestamp": 1698951286.4832501,
            "trxs": [],
            "proof": 0,
            "previous_hash": ""
        }]
        self.current_trxs = []
        self.nodes = set()
        self.client_id = time()
        self.nodes.add('localhost:5000')

    def new_trx(self, sender, recipient, amount , ts):
        self.current_trxs.append({
            "sender": sender,
            "recipient": recipient,
            "amount": amount,
            "ts" : ts
        })
        
        return self.last_block["index"] + 1

    def create_block(self):
        proof = 1
        endProsses = False
        ts = time()
        while endProsses is False:
            block = {
                "index": len(self.chain) + 1,
                "timestamp": ts,
                "trxs": [*self.current_trxs, {"sender": "", "recipient": self.client_id, "amount": 20, }],
                "proof": proof,
                "previous_hash": self.hash(self.chain[-1])
            }
            if self.valid_proof(block):
                self.current_trxs = []
                self.chain.append(block)
                return block
            else:
                proof = proof + 1

    def add_node(self, address):
        parsed_node = urlparse(address)
        self.nodes.add(parsed_node.netloc)

    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            if block['previous_hash'] != self.hash(last_block):
                return False
            if self.valid_proof(block) == False:
                return False

            last_block = block
            current_index += 1

        return True

    def consensus(slef):
        nodes = slef.nodes
        new_chain = None
        max_length = len(slef.chain)

        for node in nodes:
            res = requests.get(f'http://{node}/chain')
            if res.status_code == 200:
                length = res.json()['length']
                chain = res.json()['chain']
            if length > max_length and slef.valid_chain(chain):
                new_chain = chain
                max_length = length

        if new_chain:
            slef.chain = new_chain
            return True

        return False

    def valid_proof(self, block):
        block_hash = self.hash(block)
        return block_hash[:4] == "0000"

    def update_trx_list(self, block_trxs):
        if len(self.current_trxs) > 0:
            for bt in block_trxs:
                for t in self.current_trxs:
                    if t == bt:
                        self.current_trxs.remove(t)
        return self.current_trxs

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]
