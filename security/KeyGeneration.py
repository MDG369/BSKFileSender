import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes, padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

PRIVATE_KEY_LOCATION = "keys/private_key/private_key.pem"
PUBLIC_KEY_LOCATION = "keys/public_key/public_key.pem"


class Keys:

    def __init__(self):
        self.private_key = None
        self.public_key = None
        self.session_key = None
        self.password = b"admin"

        # creating local key from password
        digest = hashes.Hash(hashes.SHA256())
        digest.update(self.password)
        self.local_key = digest.finalize()
        self.iv = b'\x80\xae\xfe*\xc3g\x18\xc0J\xb3\xc8N\x81LR('
        self.readKeyPair()

    def generateKeyPair(self):
        self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.public_key = self.private_key.public_key()
        with open(PUBLIC_KEY_LOCATION, 'xb') as key_file:
            public_pem = self.public_key.public_bytes(encoding=serialization.Encoding.PEM,
                                                      format=serialization.PublicFormat.SubjectPublicKeyInfo)
            key_file.write(public_pem)
        with open(PRIVATE_KEY_LOCATION, 'xb') as key_file:
            private_key_encrypted = self.encryptPrivateKey(
                self.private_key.private_bytes(encoding=serialization.Encoding.PEM,
                                               format=serialization.PrivateFormat.PKCS8,
                                               encryption_algorithm=serialization.NoEncryption()))
            key_file.write(private_key_encrypted)

    def readKeyPair(self):
        try:
            key_file = open(PUBLIC_KEY_LOCATION, 'rb')
            self.decryptPrivateKey()
            self.public_key = serialization.load_pem_public_key(
                key_file.read(),
                backend=default_backend())

        except IOError:
            self.generateKeyPair()

    def encryptPrivateKey(self, private_key_bytes):
        # Pad the private key bytes to match AES block size
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(private_key_bytes) + padder.finalize()
        # Create an AES cipher with CBC mode
        cipher = Cipher(algorithms.AES(self.local_key), modes.CBC(self.iv))
        encryptor = cipher.encryptor()
        # Encrypt the padded data
        private_key_encrypted = encryptor.update(padded_data) + encryptor.finalize()
        return private_key_encrypted

    def decryptPrivateKey(self):
        try:
            key_file = open(PRIVATE_KEY_LOCATION, 'rb')
            ciphertext = key_file.read()
            # Create an AES cipher decryptor with CBC mode
            cipher = Cipher(algorithms.AES(self.local_key), modes.CBC(self.iv))
            decryptor = cipher.decryptor()
            decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
            # Unpad the private key bytes
            unpadder = padding.PKCS7(128).unpadder()
            unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()

            self.private_key = serialization.load_pem_private_key(unpadded_data,
                                                                  password=None,
                                                                  backend=default_backend())
            print(unpadded_data)
        except FileNotFoundError:
            return

    def generateSessionKey(self):
        pass
