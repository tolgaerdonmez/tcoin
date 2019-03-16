from wallet import Wallet

class Transaction():
    # sender and receiver's public keys in class format
    def __init__(self, sender, input, receiver, output, miner = None, tx_fee = 0, sig = None, genesis_tx = False):
        self.input = (sender,input)
        self.output = (receiver,output)

        self.tx_fee = tx_fee
        self.miner = miner
        #calculates fee
        tx_fee = input - output
        if tx_fee > 0:
            self.tx_fee = tx_fee

        self.sender = sender
        self.receiver = receiver

        #default is None
        self.sig = sig
        self.genesis_tx = genesis_tx

    def sign(self, wallet):
        sig, is_signed = wallet.sign(self.__gather(), wallet.chain)
        if not is_signed:
            return False
        self.sig = sig
        return True

    def __gather(self):
        if self.tx_fee > 0:
            return [self.input,self.output,(self.miner,self.tx_fee)]
        return [self.input,self.output]

    def to_dict(self):
        # if it is not the genesis tx get the sender key and signature
        if self.genesis_tx:
            receiver = Wallet.get_pu_ser(self.receiver)[1]
            dict = {'sender':self.sender,
                'input':self.input[1],
                'receiver': receiver,
                'output':self.output[1],
                'miner':self.miner,
                'tx_fee':self.tx_fee,
                'sig':self.sig
                }
            return dict 
        sender = Wallet.get_pu_ser(self.sender)[1]
        sig = Wallet.convert_sig(self.sig)
        receiver = Wallet.get_pu_ser(self.receiver)[1]
        miner = Wallet.get_pu_ser(self.miner)[1]
        dict = {'sender':sender,
                'input':self.input[1],
                'receiver': receiver,
                'output':self.output[1],
                'miner':miner,
                'tx_fee':self.tx_fee,
                'sig':sig
                }
        return dict

    @staticmethod
    def from_dict(dict):
        sender = Wallet.load_pu(Wallet.join_ser_text("public",dict['sender']))
        receiver = Wallet.load_pu(Wallet.join_ser_text("public",dict['receiver']))
        miner = Wallet.load_pu(Wallet.join_ser_text("public",dict['miner']))
        sig = Wallet.convert_sig(dict['sig'])
        tx = Transaction(
            sender = sender,
            input = dict['input'],
            receiver = receiver,
            output = dict['output'],
            miner = miner,
            tx_fee = dict['tx_fee'],
            sig = sig
        )
        # tx = Transaction(sender, dict['input'], receiver, dict['output'], sig)
        return tx


