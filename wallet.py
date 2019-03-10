from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
import hashlib

class Wallet():

    def __init__(self, load = None):
        if not load:
            self.private_key, self.public_key, self.private_key_ser, self.public_key_ser = self.__generate_keys()
        else:
            self.private_key, self.public_key, self.private_key_ser, self.public_key_ser = self.__load_keys(load)

        self.public_key_text = str(self.public_key_ser, 'utf-8').replace("-----BEGIN PUBLIC KEY-----","").replace("-----END PUBLIC KEY-----","")
        self.private_key_text = str(self.private_key_ser, 'utf-8').replace("-----BEGIN PRIVATE KEY-----","").replace("-----END PRIVATE KEY-----","")

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

    @staticmethod
    def sign(message, private):
        message = bytes(str(message), 'utf-8')
        sig = private.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return sig

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

   

# w = Wallet(b'-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDYpvUHRL0CIsNk\nkSBns6siZ6spDKsSBRl+OrROdExDSfJmEX86jGQEMFENDlDKntlPWefmoFdz6K7r\nmZXAYDVeaHfrMRIRtPpov4d4TeRDPFjFQDKog0dzuaydbW9/EdOOKMJKxqJzNhuw\nT9NFzJnTBDIyaqK5DLxnZpJ6Zq4MVmXamVqUcU3mSWcXwo3uTZKlWUk2tyDVsZZx\nb3iUX1jvYpBeD9l9eb27+FkH0vbc2I6lLTKSi7BPs45XNBUGikL2UWBuFKgPVeKq\nfONSgBWnJdnmohXAyaMO994ePyJcHU7q0B8qkfk7hbbnCM1MokFykHDOKgTTf3aF\nEvTi7n3RAgMBAAECggEAIhe7zUYC3DguOUAhMlByqLpZk98beH128oc4YnQooBod\n2/P66nK3NnWH+576FbiDh9olBQTMXkAKbqa/iwNYwp9753XUWxb4pM0m+0Z+mhn/\n+iJNFnl6H/ri7+8NsZhTizZcxLmXTLwCBW+6VmyI9EzfvVFMhAQ+DaN1f29zChuw\nSQtgMxDl9piDHLKgCcHn19O+JZWah9QuJ+xpSIqSE7SeOcfUbrW3uBMLsk5wHkbZ\n763jgN/WRlBUmwfO5RTrhI9qtwc/Zb/6OJGuFfiGeCs5HeYma3gMorQm2NvcAOgg\nFz/gI0jtsZojaRXW6fpzFGuSRv1Z1z27TTaCaNpPxQKBgQDzJ9s5YEhRC/7Qohdy\nL/dgJRxSRJpwzMCks8vKYNO4rhTA5U8eoyDOfphgN+OHbga3Lmc2OYHCDybalsb4\nAeFhBUP+kwmYzUYMMsK5ojQIxaafQ8i9H44Vxq33HAZls+ZAONbZesYCc87QmfTV\nhi3ZpBxzahfx3wXOiHo+mwyUDwKBgQDkGLMHGpCsPXKVvAxYxhuTPjG+ybTTP4Jo\nXhTX9HLpZtgNOLVBoO2QchrYbyv317KiQUi5YZHIkSjqYNKKydVs0IkkoYd2TG24\nHtBDkBx6e26qPMt8rqzRGuSC7AMlvSM/qWkdfoV3kt7Qk0vR2aJG605dl1CIc9pU\nFhHVQD5wHwKBgQDwI6iqXaCOCl66BZtKNn0FAyGZTg+I325SOw9E66OtfJ8acl1V\nUJ4R0Y0DWa7oDY2sU7OzJdA0q2of71DJlnHTs7OXM/gCZJiNa4RMeRkSoMESAYu6\n2/MjJnig15ip0KXRP1FQr6PmwCC8e5AFYOLfUuiWQ20qfqvpcXfpZI9jmQKBgH7b\noc4knyu8LRtL7837uGBm6cHDavdGTh//mzYUNUjMMwL/dAehGh8I5xdSlTCNXUNS\nbcD0m+DhotDfspkP8cxIGs4trCpGDYumT4wT/VK9jWnO0BlzCJhvjYGnA4UcsRr5\n/IUz1cUQAS4djcCTeuZYfkgdHOQXEulLMPXaeh9fAoGBAOZAwWwhOw5PPIrxemFf\ndqjbJm1GBwnSXgDZelxz1JgeVUt4wklU5h38e+tdXzR15A0mjRcEzHdeIkSJ1Iw+\nsmQ/mUwORTLErxzhv1WPNnDTHs30FpbFDIqZ6Z1rvZdsIQQmigp2j+YNgsFVh69a\ngQaKONMIOhmbL0V15mYl5bxP\n-----END PRIVATE KEY-----\n')
# w = Wallet()
# msg = "tolga"
# sig = Wallet.sign(msg,w.private_key)
# print(w.private_key_ser)
