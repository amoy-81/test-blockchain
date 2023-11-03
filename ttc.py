import hashlib
import json
from time import time
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
            print(proof)
            block = {
                "index": len(self.chain) + 1,
                "timestamp": ts,
                "trxs": self.current_trxs,
                "proof": proof,
                "previous_hash": self.hash(self.chain[-1])
            }
            if self.valid_proof(block):
                self.current_trxs = []
                self.chain.append(block)
                return block
            else:
                proof = proof + 1

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


@app.route("/main")
def main():
    new_block = blockchain.create_block()
    res = {
        "message": "The new block was successfully mined",
        "block": new_block
    }
    return jsonify(res), 201
