from wallet import Wallet

class Transaction():
    # sender and receiver's public keys
    def __init__(self, sender, input, receiver, output, sig = None):
        self.input = (sender,input)
        self.output = (receiver,output)
        self.sender = sender
        self.receiver = receiver
        #default is None
        self.sig = sig

    def sign(self, sender_pr):
        self.sig = Wallet.sign(self.__gather(),sender_pr)

    def __gather(self):
        return [self.input,self.output]

    def to_dict(self):
        dict = {'sender':self.sender,
                'input':self.input[1],
                'receiver': self.receiver,
                'output':self.input[1],
                'sig':self.sig
                }
        return dict

    @staticmethod
    def from_dict(dict):
        tx = Transaction(dict['sender'],dict['input'],dict['receiver'],dict['output'],dict['sig'])
        return tx


