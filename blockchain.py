import datetime
import hashlib
import json
import requests
from urllib.parse import urlparse    
import time

def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        print (f'{(te - ts)} ms')
        return result
    return timed

class Block():

    def __init__(self, index = 0, previous_hash = '0', transactions = [], nodes = [], type = 'transaction_block', timestamp = None, hash = None, proof = None, protocol_name = None):
        
        self.index = index
        self.timestamp = str(datetime.datetime.now())
        if timestamp != None:
            self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.height = len(self.transactions)
        encoded_block = (str(self.index) + self.timestamp + self.previous_hash + str(self.transactions)).encode()
        self.hash = hashlib.sha256(encoded_block).hexdigest()
        if hash != None:
            self.hash = hash
        self.proof = proof
        self.nodes = nodes
        self.type = type# transaction_block save_block genesis_block
        self.protocol_name = protocol_name
    
    def to_dict(self):
        block_dic = {
            'index':self.index,
            'timestamp':self.timestamp,
            'previous_hash':self.previous_hash,
            'transactions':self.transactions,
            'hash':self.hash,
            'proof':self.proof,
            'nodes':self.nodes,
            'height':self.height,
            'type':self.type,
            'protocol_name':self.protocol_name
        }
        return block_dic

    @staticmethod
    def from_dict(block_dict):
        block = Block(block_dict['index'],block_dict['previous_hash'],block_dict['transactions'],block_dict['nodes'], block_dict['type'], block_dict['timestamp'], block_dict['hash'], block_dict['proof'], block_dict['protocol_name'])
        return block

    def cal_hash(self):
        encoded_block = (str(self.index) + self.timestamp + self.previous_hash + str(self.transactions)).encode()
        hash = hashlib.sha256(encoded_block).hexdigest()
        return hash

class Blockchain:

    def __init__(self,protocol_name = "undefined"):
        self.protocol_name = protocol_name
        self.chain = []
        self.transactions = []
        self.nodes = set()
        self.difficulty = '0000'
        #Loading the blockchain.json if exists 
        self.load_chain_from_json()


    def load_chain_from_json(self):
        try:
            # with open("blockchain.json",'r') as f:
            #     loaded_chain = json.load(f)
            # loaded_chain = self.load_chain()
            with open("blockchain.json",'r') as f:
                dict_chain = json.load(f)
                loaded_chain = self.dict_to_chain(dict_chain)
                if loaded_chain[0].protocol_name != None and loaded_chain[0].protocol_name == self.protocol_name:
                    self.chain = loaded_chain
                    # adding nodes
                    for node in self.chain[-1].nodes:
                        self.nodes.add(node)
                else:
                    raise FileNotFoundError
        except FileNotFoundError:
            # creating the genesis block 
            # no transaction
            self.create_block(index = 0, proof= 1, previous_hash='0', type = 'genesis_block')

    def dict_to_chain(self,dict_chain):
        class_chain = []
        for block in dict_chain:
            loaded_block = Block.from_dict(block)
            class_chain.append(loaded_block)
        return class_chain

    def chain_to_dict(self):
        dict_chain = []
        for block in self.chain:
            dict_chain.append(block.to_dict())
        return dict_chain

    def save_chain_to_json(self):
        with open("blockchain.json",'w') as f:
            dict_chain = []
            for block in self.chain:
                dict_chain.append(block.to_dict())
            f.writelines(json.dumps(dict_chain, sort_keys=True, indent=4))

    def create_block(self, type, index = 0, proof = 1, previous_hash='0'):

        if type == 'genesis_block':
            previous_hash = previous_hash
        else:
            previous_hash = self.last_block().hash
        new_block = Block(
            index = len(self.chain) + 1,
            previous_hash = previous_hash,
            transactions = self.transactions,
            nodes = list(self.nodes),
            type = type,
            protocol_name = self.protocol_name
            )
        self.transactions = []
        new_block.proof = self.proof_of_work(new_block)
        self.chain.append(new_block)

        self.save_chain_to_json()
        return new_block

    def last_block(self):
        return self.chain[-1]

    @timeit
    def proof_of_work(self, block):
        check_proof = False
        proof = 0
        while check_proof == False:
            hash_operation = hashlib.sha256(str(block.hash + str(proof)).encode()).hexdigest()
            if hash_operation[:len(self.difficulty)] == self.difficulty:
                check_proof = True
            else:
                proof += 1
        return proof

    def is_chain_valid(self,chain):
        index = 1
        while index < len(chain):
            previous_block = chain[index-1]
            current_block = chain[index]
            if current_block.previous_hash != previous_block.hash:
                return False
            hash_operation = hashlib.sha256(str(current_block.hash + str(current_block.proof)).encode()).hexdigest()
            if hash_operation[:len(self.difficulty)] != self.difficulty:
                return False
            index+=1
        return True

    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({'sender':sender,
                                  'receiver': receiver,
                                  'amount': amount})
        previous_block = self.last_block()
        return previous_block.index + 1

    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                dict_chain = response.json()['chain']
                chain = self.dict_to_chain(dict_chain)
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        # if the longest_chain is not none
        if longest_chain:
            self.chain = longest_chain
            self.save_chain_to_json()
            return True
        else:
            return False


# if __name__ == "__main__":
#     pass