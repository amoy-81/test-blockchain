import hashlib
import json
import requests
from time import time
from urllib.parse import urlparse
from flask import Flask, jsonify, request
from blockchainـobject import Blockchain

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

    # send block for nodes
    nodes = blockchain.nodes
    for node in nodes:
        res = requests.post(f'http://{node}/blockaccept', json=new_block)

    res = {
        "message": "The new block was successfully mined",
        "block": new_block
    }
    return jsonify(res), 201


@app.route("/nodes/register", methods=["POST"])
def register_node():
    # example input {node : "http://0.0.0.0:6000"}

    # send a request for add address in nodes list
    address = request.get_json()
    nodes = blockchain.nodes

    last_node_list = blockchain.nodes
    max_length = len(last_node_list)
    for n in nodes :
        response = requests.post(f"http://{n}/nodes/add", json={"address": address['node']})
        if response.status_code == 201:
            print(len(response.json()['nodes']) > max_length)
            print(response.json()['nodes'])
            if len(response.json()['nodes']) > max_length :
                last_node_list = response.json()['nodes']

    # if response ok add add received nodes to the list of nodes
    for node in last_node_list:
        blockchain.nodes.add(node)

    res = {
        "message": "New nodes added successfully",
        "total_nodes": list(blockchain.nodes)
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
                res = requests.post(f'http://{node}/blockaccept', json=block)
            res = {
                "message": "block added to my chain"
            }

            return jsonify(res), 200

    return jsonify({"message": "block not is valid"})


if __name__ == "__main__":
    app.run(host="0.0.0.0")


# nodes ok
# bug node downing
