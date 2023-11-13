import hashlib
import json
import requests
from time import time
from urllib.parse import urlparse
from flask import Flask, jsonify, request
from blockchainـobject import Blockchain

# main node address http://127.0.0.1:5000/

blockchain = Blockchain()

app = Flask(__name__)


@app.route("/trx/new", methods=["POST"])
def create_trx():
    body = request.get_json()
    index = int(blockchain.chain[-1]['index']) + 1
    ts = time()
    new_trx = blockchain.new_trx(
        body["sender"], body["recipient"], body["amount"], ts)

    nodes = blockchain.nodes
    for n in nodes:
        try:
            response = requests.post(f'http://{n}/trx/share', json={
                "sender": body["sender"], "recipient": body["recipient"], "amount": body["amount"], "ts": ts})
        except:
            print(n)

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

    # send block for nodes
    nodes = blockchain.nodes
    for node in nodes:
        try:
            res = requests.post(f'http://{node}/blockaccept', json=new_block)
        except:
            print(node)

    res = {
        "message": "The new block was successfully mined",
        "block": new_block
    }
    return jsonify(res), 201


@app.route("/nodes/add", methods=["POST"])
def add_new_node():
    # example input {node : "http://0.0.0.0:6000"}

    # get node address and add to list and send nodes
    address = request.get_json()

    # add node in nodes list
    blockchain.add_node(address["address"])

    # remove sender node from node lists
    nodes_list = list(blockchain.nodes)
    parsed_node = urlparse(address["address"])
    nodes_list.remove(parsed_node.netloc)

    res = {
        "message": "New nodes added successfully",
        "nodes": nodes_list
    }
    return jsonify(res), 201


@app.route("/nodes/consensus")
def nodes_consensus():
    replace = blockchain.consensus()
    res = {
        "message": "The chain is completed",
        "new_chain": blockchain.chain
    }
    return jsonify(res), 200

# add new trx in current_trx and sen for nodes


@app.route("/trx/share", methods=["POST"])
def share_new_trx():
    new_trx = request.get_json()
    exist_trx = False
    for t in blockchain.current_trxs:
        if new_trx == t:
            exist_trx = True
            break
    if exist_trx == False:
        add_result = blockchain.current_trxs.append(new_trx)

        for node in blockchain.nodes:
            try:
                res = requests.post(f'http://{node}/trx/share', json=new_trx)
            except:
                print(node)
        return jsonify({"message": "trx successfuly add in current trxs"}), 201
    else:
        return jsonify({"message": "trx is already exists"})


@app.route("/blockaccept", methods=["POST"])
def accept_newblock():
    block = request.get_json()
    last_block = blockchain.chain[-1]

    # validation new block
    if block['previous_hash'] == blockchain.hash(last_block):
        if blockchain.valid_proof(block) == True:
            # update trxs list
            block_trxs = block["trxs"]
            update_result = blockchain.update_trx_list(block_trxs)
            # add block in chain
            blockchain.chain.append(block)

            # send new block for nodes
            nodes = blockchain.nodes
            for node in nodes:
                try:
                    res = requests.post(
                        f'http://{node}/blockaccept', json=block)
                except:
                    print(node)
            res = {
                "message": "block added to my chain"
            }

            return jsonify(res), 200

    return jsonify({"message": "block not is valid"})


if __name__ == "__main__":
    app.run(host="0.0.0.0")
