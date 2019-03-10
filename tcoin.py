from blockchain import Blockchain,Block
from wallet import Wallet
from transaction import Transaction
from flask import Flask, jsonify, request, render_template, flash, redirect, url_for, send_file, Session
from uuid import uuid4
import json
import sys
import forms
import requests
from functools import wraps
from urllib.parse import urlparse 
from zipfile import ZipFile
from io import BytesIO
from pathlib import Path
from datetime import datetime
import os

#temporary wallet
user_wallet = Wallet(b'-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDYpvUHRL0CIsNk\nkSBns6siZ6spDKsSBRl+OrROdExDSfJmEX86jGQEMFENDlDKntlPWefmoFdz6K7r\nmZXAYDVeaHfrMRIRtPpov4d4TeRDPFjFQDKog0dzuaydbW9/EdOOKMJKxqJzNhuw\nT9NFzJnTBDIyaqK5DLxnZpJ6Zq4MVmXamVqUcU3mSWcXwo3uTZKlWUk2tyDVsZZx\nb3iUX1jvYpBeD9l9eb27+FkH0vbc2I6lLTKSi7BPs45XNBUGikL2UWBuFKgPVeKq\nfONSgBWnJdnmohXAyaMO994ePyJcHU7q0B8qkfk7hbbnCM1MokFykHDOKgTTf3aF\nEvTi7n3RAgMBAAECggEAIhe7zUYC3DguOUAhMlByqLpZk98beH128oc4YnQooBod\n2/P66nK3NnWH+576FbiDh9olBQTMXkAKbqa/iwNYwp9753XUWxb4pM0m+0Z+mhn/\n+iJNFnl6H/ri7+8NsZhTizZcxLmXTLwCBW+6VmyI9EzfvVFMhAQ+DaN1f29zChuw\nSQtgMxDl9piDHLKgCcHn19O+JZWah9QuJ+xpSIqSE7SeOcfUbrW3uBMLsk5wHkbZ\n763jgN/WRlBUmwfO5RTrhI9qtwc/Zb/6OJGuFfiGeCs5HeYma3gMorQm2NvcAOgg\nFz/gI0jtsZojaRXW6fpzFGuSRv1Z1z27TTaCaNpPxQKBgQDzJ9s5YEhRC/7Qohdy\nL/dgJRxSRJpwzMCks8vKYNO4rhTA5U8eoyDOfphgN+OHbga3Lmc2OYHCDybalsb4\nAeFhBUP+kwmYzUYMMsK5ojQIxaafQ8i9H44Vxq33HAZls+ZAONbZesYCc87QmfTV\nhi3ZpBxzahfx3wXOiHo+mwyUDwKBgQDkGLMHGpCsPXKVvAxYxhuTPjG+ybTTP4Jo\nXhTX9HLpZtgNOLVBoO2QchrYbyv317KiQUi5YZHIkSjqYNKKydVs0IkkoYd2TG24\nHtBDkBx6e26qPMt8rqzRGuSC7AMlvSM/qWkdfoV3kt7Qk0vR2aJG605dl1CIc9pU\nFhHVQD5wHwKBgQDwI6iqXaCOCl66BZtKNn0FAyGZTg+I325SOw9E66OtfJ8acl1V\nUJ4R0Y0DWa7oDY2sU7OzJdA0q2of71DJlnHTs7OXM/gCZJiNa4RMeRkSoMESAYu6\n2/MjJnig15ip0KXRP1FQr6PmwCC8e5AFYOLfUuiWQ20qfqvpcXfpZI9jmQKBgH7b\noc4knyu8LRtL7837uGBm6cHDavdGTh//mzYUNUjMMwL/dAehGh8I5xdSlTCNXUNS\nbcD0m+DhotDfspkP8cxIGs4trCpGDYumT4wT/VK9jWnO0BlzCJhvjYGnA4UcsRr5\n/IUz1cUQAS4djcCTeuZYfkgdHOQXEulLMPXaeh9fAoGBAOZAwWwhOw5PPIrxemFf\ndqjbJm1GBwnSXgDZelxz1JgeVUt4wklU5h38e+tdXzR15A0mjRcEzHdeIkSJ1Iw+\nsmQ/mUwORTLErxzhv1WPNnDTHs30FpbFDIqZ6Z1rvZdsIQQmigp2j+YNgsFVh69a\ngQaKONMIOhmbL0V15mYl5bxP\n-----END PRIVATE KEY-----\n')

#Getting the config.json file
config = None
miner_wallet = None
config_template = {"protocol_name":"TCOIN_BLOCKCHAIN_NETWORK","miner":"your_miner_private_key","secret_key":"TCOIN_BLOCKCHAIN_NETWORK","node_address":"null"}
# config = {"protocol_name":"TCOIN_BLOCKCHAIN_NETWORK","miner":"your_miner_adress_or_name","secret_key":"TCOIN_BLOCKCHAIN_NETWORK","node_address":"null"}

config_path = "config.json" #sys.argv[3]
try:
    host = sys.argv[1]
    port = sys.argv[2]
except:
    host = 'localhost'
    port = 5000

def save_config():
    with open(config_path,'w') as file:
        file.writelines(json.dumps(config, sort_keys=True, indent=4))

try:
    with open(config_path,'r') as file:
        loaded_config = json.load(file)
        if config_template == loaded_config:
            raise FileNotFoundError
        config = loaded_config
        miner_wallet = Wallet(config['miner'].encode())
except FileNotFoundError:
    with open(config_path,'w') as file:
        file.writelines(json.dumps(config_template, sort_keys=True, indent=4))
    print("No config file detected. Creating a new one and a new wallet for the miner")
    # creating the config
    config = config_template
    # creating the new wallet
    miner_wallet = Wallet()
    # saving the pr key to the config
    config['miner'] = str(miner_wallet.private_key_ser, 'utf-8')
    save_config()
    input("Please relaunch\nPress any key to continue...")
    sys.exit()

app = Flask(__name__)

app.secret_key = config["secret_key"] 
#creating address for the node
node_address = str(uuid4()).replace('-','')
#creating the blockchain with the name from the config file
blockchain = Blockchain(config['protocol_name'])

def mine_save_block():
    block = blockchain.create_block(index = blockchain.last_block().index + 1,type = 'save_block')
    return block

def broadcast_transaction(tran = None,clear = False):
     # broadcasting the new transaction
    if clear and len(blockchain.nodes) > 1:
        for node in blockchain.chain[-1].nodes:
            # avoiding duplicate transaction
            if node != config['node_address']:
                requests.get('http://'+node+'/clear_transactions')
    elif len(blockchain.nodes) > 1: 
        for node in blockchain.chain[-1].nodes:
            # avoiding duplicate transaction
            if node != config['node_address']:
                requests.post('http://'+node+'/add_transaction',json={"sender": tran[0],"receiver":tran[1],"amount":tran[2]})

def node_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        
        if not config['node_address'] in blockchain.nodes:
            flash("You need to join the network before doing operations...","warning")
            return redirect(url_for("join_network"))
        else:
            return f(*args, **kwargs)
    return decorated_function

def check(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not blockchain.is_chain_valid(blockchain.chain):
            flash("Invalid blockchain oops...","warning")
            return redirect(url_for("index"))
        else:
            return f(*args, **kwargs)
    return decorated_function

@app.route('/cur_transactions', methods = ["GET"])
def current_transactions():
    transactions = blockchain.transactions
    return render_template("current_transactions.html",transactions = transactions)

@app.route('/mine_block', methods = ['GET'])
@check
@node_required
def mine_block():
    if blockchain.transactions == []:
        flash("No transactions, can't mine the block...","warning")
        return redirect(url_for("index"))

    # giving miner's gift > creating new transaction
    # HANDLE THIS LATERRRRRRR !!!!!!!!
        # blockchain.add_transaction(sender = node_address, receiver = config["miner"], amount = 1)

    # broadcasting that the transactions are cleared !!!
    block = blockchain.create_block('transaction_block',blockchain.last_block().index + 1)
    broadcast_transaction(clear=True)
  
    return redirect(f"block/{block.index}")

@app.route('/get_chain', methods = ['GET'])
@check
def get_chain():
    response = {'chain': blockchain.chain_to_dict(),
                'length': len(blockchain.chain)}
    return jsonify(response), 200

@app.route('/blockchain', methods = ['GET'])
def show_blockchain():
    return render_template("blockchain.html",chain = blockchain.chain)

@app.route('/block/<string:index>', methods = ["GET"])
def block_detail(index):
    index = int(index)
    if index > len(blockchain.chain):
        flash(f"There is no block such as #{index}","warning")
        return redirect(url_for("index"))
    if index == 0:
        flash(f"There is no block such as #{index} showing the last block","warning")
    block = blockchain.chain[index-1]
    return render_template("block.html",block = block)

@app.route('/is_valid',methods = ['GET'])
@node_required
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if(is_valid):
        response = {'message':'All good.The Blockchain is valid.'}
    else:
        response = {'message':'Oops, something went wrong !'}
    return  jsonify(response), 200

@app.route('/add_transaction', methods = ['POST'])
@check
@node_required
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'input', 'receiver', 'output']
    if not all (key in json for key in transaction_keys):
        return 'Invalid transaction, some elements are missing !', 400

    #creating new transaction
    new_tx = Transaction(user_wallet.public_key, json['input'], miner_wallet.public_key, json['output'])
    new_tx.sign(user_wallet.private_key)
    index = blockchain.add_transaction(new_tx)

    response = {'message':f'This transaction will be added to Block {index}'}
    return  jsonify(response), 201

@app.route('/clear_transactions',methods = ['GET'])
@node_required
def clear_transactions():
    blockchain.transactions = []
    return jsonify("Cleared!"),200

#connecting new nodes
@app.route('/connect_node', methods=['POST'])
@node_required
def connect_node():
    json = request.get_json()
    nodes = json.get("nodes")
    if nodes is None:
        return "No node", 400
    for node in nodes:
        blockchain.add_node(node)
    # response = {'message': 'All the nodes are now connected. The TCoin Blockchain now contains these nodes:',
    #             'total_nodes': list(blockchain.nodes)}
    return redirect("/mine_block"), 200

@app.route('/replace_chain',methods = ['GET'])
@node_required
def replace_chain():
    is_replaced = blockchain.replace_chain()
    if(is_replaced):
        flash('The Blockchain is replaced with the longest chain.',"success")
    else:
        flash('All good the chain is the longest one.',"success")

    return  redirect(url_for("show_blockchain"))

@app.route('/check_saved_chain', methods = ['GET'])
@node_required
def check_saved_chain():
    with open("blockchain.json", 'r') as f:
        loaded_chain = json.load(f)
    if loaded_chain == blockchain.chain_to_dict():
        response = {'message':'The chain is same with the saved one'}
        return jsonify(response), 200
    else:
        response = {'message':'The chain is not same with the saved one !!!'}
        return jsonify(response), 400

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/send_tcoin", methods = ["GET","POST"])
@check
@node_required
def send_tcoin():
    form = forms.AddTransaction(request.form)
    if request.method == "GET":
        return render_template("send_tcoin.html",form = form)
    else:
        if form.output.data > form.input.data or (not form.input.data > 0):
            flash('Invalid amount please enter an amount larger than 0...','danger')
            return redirect(url_for("send_tcoin"))
        
        # index = blockchain.add_transaction(form.sender.data, form.receiver.data, form.amount.data)
        new_tx = Transaction(user_wallet.public_key, form.input.data, miner_wallet.public_key, form.output.data)
        new_tx.sign(user_wallet.private_key)
        index = blockchain.add_transaction(new_tx)
        # broadcasting the new transaction to other transaction pools on nodes
        # new_transaction = [form.sender.data,form.receiver.data,form.amount.data]
        # broadcast_transaction(new_transaction)

        flash(f'This transaction will be added to Block {index}','success')
        return redirect("/cur_transactions")

@app.route("/is_node_active", methods = ["GET"])
def is_node_active():
    return jsonify(config['protocol_name']),200

@app.route("/join_network", methods = ["GET","POST"])
def join_network():
    form = forms.AddNode(request.form)
    if request.method == "GET":
        return render_template("join_network.html",form = form)
    else:
        try:
            get = requests.get('http://'+urlparse(form.address.data).netloc+'/is_node_active')
            if urlparse(form.address.data).netloc.split(":")[0] == "localhost":
                raise TypeError
            if urlparse(form.address.data).netloc in blockchain.nodes:
                flash("You've already joined the network !","warning")
                return redirect(url_for("index"))
            
            if get.status_code == 200 and json.loads(get.text) == config['protocol_name']:
                blockchain.add_node(form.address.data)
                # setting the node address in config
                config['node_address'] = urlparse(form.address.data).netloc
                save_config()
                # broadcasting to other nodes
                if len(blockchain.nodes) > 1: 
                    for node in blockchain.chain[-1].nodes:
                        requests.post('http://'+node+'/connect_node',json={"nodes": [form.address.data]})

                new_block = mine_save_block()
                flash(f"You joined the network, save block mined !, block #{new_block.index}","success")
                # saving the new nodes on the blockchain
                
                return redirect(f"/block/{new_block.index}")
        except:
            flash("Inactive or invalid address ","danger")
            return redirect(url_for("join_network"))

@app.route('/download-protocol')
@check
def request_zip():
    base_path = Path('./')
    file_list = []
    for dirpath,_,filenames in os.walk(base_path):
        if dirpath == '.':
            for file in filenames: 
                if file != "config.json":
                    file_list.append("./" + file)
        elif dirpath == "./templates":
            file_list.append('./templates')
            for file in filenames:
                file_list.append("./templates/" + file)
        elif dirpath == "./templates/includes":
            file_list.append('./templates/includes')
            for file in filenames:
                file_list.append("./templates/includes/" + file)

    data = BytesIO()
    with ZipFile(data, mode='w') as z:
        for file in file_list:   
            z.write(file)
    data.seek(0)

    return send_file(
        data,
        mimetype='application/zip',
        as_attachment=True,
        attachment_filename=f"{config['protocol_name']}-{datetime.now()}.zip"
    )

@app.route('/network', methods = ["GET"])
def show_network():
    nodes = blockchain.nodes
    return render_template("network.html",nodes = nodes)


if __name__ == '__main__':
    app.run(debug=False,host=host,port=port)

