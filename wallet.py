from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
import hashlib

class Wallet():

    def __init__(self, load = None, chain = None):
        self.coins = None
        if not load:
            self.private_key, self.public_key, self.private_key_ser, self.public_key_ser = self.__generate_keys()
        else:
            self.private_key, self.public_key, self.private_key_ser, self.public_key_ser = self.__load_keys(load)
        self.chain = chain
        # self.public_key_text = str(self.public_key_ser, 'utf-8').replace("-----BEGIN PUBLIC KEY-----","").replace("-----END PUBLIC KEY-----","")
        # self.private_key_text = str(self.private_key_ser, 'utf-8').replace("-----BEGIN PRIVATE KEY-----","").replace("-----END PRIVATE KEY-----","")

    def __generate_keys(self):
        private = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )    
        public = private.public_key()

        pu_ser = public.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        pr_ser = private.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        return private, public, pr_ser, pu_ser

    def __load_keys(self, private_key):
        private = serialization.load_pem_private_key(
            private_key,
            password=None,
            backend=default_backend()
        )

        public = private.public_key()

        pu_ser = Wallet.get_pu_ser(public)[0]
        pr_ser = Wallet.get_pr_ser(private)[0]

        return private, public, pr_ser, pu_ser

    def calculate_coins(self,chain):
        total = 0
        plus = []
        minus = []
        for block in chain:
            for tx in block.transactions:
                # tx that user give out coins
                pu = self.get_pu_ser(self.public_key)[1]
                if tx['sender'] == pu:
                    minus.append(tx['input'])
                if tx['receiver'] == pu:
                    plus.append(tx['output'])
        total = sum(plus) - sum(minus)
        return total

    def sign(self, message, chain):
        tx_input = message[0][1]
        # if the wallet doesn't have the needed amount of coins
        if self.calculate_coins(chain) - tx_input < 0:
            return None, False
        message = bytes(str(message), 'utf-8')
        sig = self.private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return sig, True

    @staticmethod
    def verify(message, sig, pu_ser):
        public = serialization.load_pem_public_key(
            pu_ser,
            backend=default_backend()
        )
        
        message = bytes(str(message), 'utf-8')
        try:
            public.verify(
                sig,
                message,
                padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            return False
        except:
            print("Error executing public_key.verify")
            return False

    @staticmethod
    def get_pu_ser(public_key):
        pu_ser = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        pu_text = str(pu_ser, 'utf-8').replace("-----BEGIN PUBLIC KEY-----","").replace("-----END PUBLIC KEY-----","")
        return (pu_ser,pu_text)

    @staticmethod
    def get_pr_ser(private_key):
        pr_ser = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        pr_text = str(pr_ser, 'utf-8').replace("-----BEGIN PRIVATE KEY-----","").replace("-----END PRIVATE KEY-----","")
        return (pr_ser,pr_text)
    
    @staticmethod
    def join_ser_text(type,key):
        type = type.upper()
        x = [f"-----BEGIN {type} KEY-----",key,f"-----END {type} KEY-----"]
        return "".join(x)

    @staticmethod
    def load_pu(key):
        pu = serialization.load_pem_public_key(key,default_backend())
        return pu

    @staticmethod
    def convert_sig(sig):
        if type(sig) == type("string"):
            return bytes([ord(x) for x in sig])
        elif type(sig) == type(b'byte'):
            return ''.join(chr(x) for x in sig)
# w = Wallet(b'-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDYpvUHRL0CIsNk\nkSBns6siZ6spDKsSBRl+OrROdExDSfJmEX86jGQEMFENDlDKntlPWefmoFdz6K7r\nmZXAYDVeaHfrMRIRtPpov4d4TeRDPFjFQDKog0dzuaydbW9/EdOOKMJKxqJzNhuw\nT9NFzJnTBDIyaqK5DLxnZpJ6Zq4MVmXamVqUcU3mSWcXwo3uTZKlWUk2tyDVsZZx\nb3iUX1jvYpBeD9l9eb27+FkH0vbc2I6lLTKSi7BPs45XNBUGikL2UWBuFKgPVeKq\nfONSgBWnJdnmohXAyaMO994ePyJcHU7q0B8qkfk7hbbnCM1MokFykHDOKgTTf3aF\nEvTi7n3RAgMBAAECggEAIhe7zUYC3DguOUAhMlByqLpZk98beH128oc4YnQooBod\n2/P66nK3NnWH+576FbiDh9olBQTMXkAKbqa/iwNYwp9753XUWxb4pM0m+0Z+mhn/\n+iJNFnl6H/ri7+8NsZhTizZcxLmXTLwCBW+6VmyI9EzfvVFMhAQ+DaN1f29zChuw\nSQtgMxDl9piDHLKgCcHn19O+JZWah9QuJ+xpSIqSE7SeOcfUbrW3uBMLsk5wHkbZ\n763jgN/WRlBUmwfO5RTrhI9qtwc/Zb/6OJGuFfiGeCs5HeYma3gMorQm2NvcAOgg\nFz/gI0jtsZojaRXW6fpzFGuSRv1Z1z27TTaCaNpPxQKBgQDzJ9s5YEhRC/7Qohdy\nL/dgJRxSRJpwzMCks8vKYNO4rhTA5U8eoyDOfphgN+OHbga3Lmc2OYHCDybalsb4\nAeFhBUP+kwmYzUYMMsK5ojQIxaafQ8i9H44Vxq33HAZls+ZAONbZesYCc87QmfTV\nhi3ZpBxzahfx3wXOiHo+mwyUDwKBgQDkGLMHGpCsPXKVvAxYxhuTPjG+ybTTP4Jo\nXhTX9HLpZtgNOLVBoO2QchrYbyv317KiQUi5YZHIkSjqYNKKydVs0IkkoYd2TG24\nHtBDkBx6e26qPMt8rqzRGuSC7AMlvSM/qWkdfoV3kt7Qk0vR2aJG605dl1CIc9pU\nFhHVQD5wHwKBgQDwI6iqXaCOCl66BZtKNn0FAyGZTg+I325SOw9E66OtfJ8acl1V\nUJ4R0Y0DWa7oDY2sU7OzJdA0q2of71DJlnHTs7OXM/gCZJiNa4RMeRkSoMESAYu6\n2/MjJnig15ip0KXRP1FQr6PmwCC8e5AFYOLfUuiWQ20qfqvpcXfpZI9jmQKBgH7b\noc4knyu8LRtL7837uGBm6cHDavdGTh//mzYUNUjMMwL/dAehGh8I5xdSlTCNXUNS\nbcD0m+DhotDfspkP8cxIGs4trCpGDYumT4wT/VK9jWnO0BlzCJhvjYGnA4UcsRr5\n/IUz1cUQAS4djcCTeuZYfkgdHOQXEulLMPXaeh9fAoGBAOZAwWwhOw5PPIrxemFf\ndqjbJm1GBwnSXgDZelxz1JgeVUt4wklU5h38e+tdXzR15A0mjRcEzHdeIkSJ1Iw+\nsmQ/mUwORTLErxzhv1WPNnDTHs30FpbFDIqZ6Z1rvZdsIQQmigp2j+YNgsFVh69a\ngQaKONMIOhmbL0V15mYl5bxP\n-----END PRIVATE KEY-----\n')
# w = Wallet()
# msg = "tolga"
# sig = Wallet.sign(msg,w.private_key)

# converting signature to string
# string = ''.join(chr(x) for x in sig)
# also decode("latin-1") converts but i dont know if that works out
# converting signature back to bytes
# new_sig = bytes([ord(x) for x in string])
# key = b"-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA3BEGOFJ4h94p11QM3Jy4\nVXEO/RzuSD2rnE3v08hQYxWqllDzBYWuregx7gMoHEUYKY5GB5AM4uuhKA+eNWsL\na2jdZOKPJA7WiEzMMcJlUgILE4L4h+cZv8ZvX/zkDl8itu3nMnN7oJj6+Q8zm9/T\nHPXW8iHRnihCvLWH5zXLMSTzG//pFbXUs4yGh2AE7sCMiYLtjYG64HY8rkb86w9C\ntW5fVoKQOyEMZG/MhVHsinGHnmWZaXX0xsxgtu0RCkjQCLAxCdtqh/YXlWw6Li0j\nsVWzB1w9dPtjboHsqcVxttlwJnEpePWprFBIjSw9B4aMJ6KbIMw6Py2V+LIOVGXj\nxQIDAQAB\n-----END PUBLIC KEY-----"
# key2 = w.public_key_ser
# print(Wallet.load_pu(key))
# print(key2,key)
# print(Wallet.load_pu(key))
