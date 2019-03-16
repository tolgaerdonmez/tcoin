from wallet import Wallet

class Transaction():
    # sender and receiver's public keys in class format
    def __init__(self, sender, input, receiver, output, miner = None, tx_fee = 0, sig = None, bonus = False):
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
        self.bonus = bonus

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
        if not self.bonus:
            sender = Wallet.get_pu_ser(self.sender)[1]
            sig = Wallet.convert_sig(self.sig)
            miner = Wallet.get_pu_ser(self.miner)[1]
        receiver = Wallet.get_pu_ser(self.receiver)[1]
        dict = {'sender':self.sender if self.bonus else sender, # if bonus send self.sender = none
                'input':self.input[1],
                'receiver': receiver,
                'output':self.output[1],
                'miner':self.miner if self.bonus else miner, # if bonus send self.miner = none
                'tx_fee':self.tx_fee,
                'sig':self.sig if self.bonus else sig # if bonus send self.sig = none // bcs. no need !
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
        return tx


