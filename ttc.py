import hashlib
import json
import requests
from time import time
from urllib.parse import urlparse
from flask import Flask, jsonify, request


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

    def new_trx(self, sender, recipient, amount):
        self.current_trxs.append({
            "sender": sender,
            "recipient": recipient,
            "amount": amount,
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
                "trxs": [*self.current_trxs , {"sender": "", "recipient": self.client_id, "amount": 20,}],
                "proof": proof,
                "previous_hash": self.hash(self.chain[-1])
            }
            if self.valid_proof(block):
                self.current_trxs = []
                self.chain.append(block)
                return block
            else:
                proof = proof + 1

    def add_node(self , address):
        print(address)
        parsed_node = urlparse(address)
        self.nodes.add(parsed_node.netloc)

    def valid_chain(self , chain):
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            if block['previous_hash'] != self.hash(last_block) :
                return False
            if self.valid_proof(block) == False :
                return False
            
            last_block = block
            current_index += 1
        
        return True

    def consensus(slef):
        nodes = slef.nodes
        new_chain = None
        max_length = len(slef.chain)

        for node in nodes :
            res = requests.get(f'http://{node}/chain')
            if res.status_code == 200:
                length = res.json()['length']
                chain = res.json()['chain']
                print(chain)
            if length > max_length and slef.valid_chain(chain):
                new_chain = chain
                max_length = length

        if new_chain :
            slef.chain = new_chain
            return True

        return False

    def valid_proof(self, block):
        block_hash = self.hash(block)
        return block_hash[:4] == "0000"

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]


blockchain = Blockchain()

app = Flask(__name__)


@app.route("/trx/new", methods=["POST"])
def create_trx():
    body = request.get_json()
    index = int(blockchain.chain[-1]['index']) + 1
    new_trx = blockchain.new_trx(
        body["sender"], body["recipient"], body["amount"])
    return jsonify({"message": f'new trx successfully created in block {index}'}), 201


@app.route("/chain")
def get_chain():
    res = {
        "chain": blockchain.chain,
        "length": len(blockchain.chain)
    }
    return jsonify(res), 200


@app.route("/mine")
def main():
    new_block = blockchain.create_block()
    res = {
        "message": "The new block was successfully mined",
        "block": new_block
    }
    return jsonify(res), 201

@app.route("/nodes/add" , methods=["POST"])
def add_new_node():
    # example input [{node : "http://0.0.0.0:6000"}]
    address = request.get_json()
    for node in address:
        blockchain.add_node(node["node"])

    res = {
        "message" : "New nodes added successfully",
        "total_nodes" : list(blockchain.nodes)
    }
    return jsonify(res) , 201

@app.route("/nodes/consensus")
def nodes_consensus():
    replace = blockchain.consensus()
    res = {
        "message":"The chain is completed",
        "new_chain" : blockchain.chain
    }
    return jsonify(res) , 200

if __name__ == "__main__":
    app.run(host="0.0.0.0")