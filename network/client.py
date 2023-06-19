import os
import socket
import time
from time import sleep
from tqdm import tqdm
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import padding as pd
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

FORMAT = "utf-8"
SIZE = 1024


def sendText(ip, port, keys, text, cipher_type="cbc"):

    """ Starting a TCP socket. """
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ADDR = (ip, port)
    """ Connecting to the server. """
    client.connect(ADDR)
    sendPublicKey(client, keys)
    sendTransferParameters(client, keys, 1, cipher_type, 1, 1)
    cipher = None
    if cipher_type == 'cbc':
        print("CLIENT: cbc")
        cipher = Cipher(algorithms.AES(keys.session_key), modes.CBC(keys.iv))
    elif cipher_type == 'ecb':
        print("CLIENT: ecb")
        cipher = Cipher(algorithms.AES(keys.session_key), modes.ECB())
    """ 'TEXT' is appended to every text message to differentiate text and file transfer """
    if text is not None:
        encrypted_text = encrypt(text, cipher)
        client.send(encrypted_text)

    """ Closing the connection from the server. """
    client.close()


def encrypt(text, cipher, barcyph=None, win=None):
    start = time.perf_counter()
    if barcyph is not None:
        barcyph["value"] = 0
        win.update_idletasks()
    padder = pd.PKCS7(128).padder()
    padded_data = padder.update(text) + padder.finalize()
    if barcyph is not None:
        barcyph["value"] = 50
        win.update_idletasks()
    encryptor = cipher.encryptor()
    ct = encryptor.update(padded_data) + encryptor.finalize()
    if barcyph is not None:
        barcyph["value"] = barcyph["maximum"]
    end = time.perf_counter()
    print(f"CLIENT: Encryption time = {end-start}")
    return ct


def sendFile(ip, port, win, barprog, barcyph, keys,  filedir=None, cipher_type="cbc", block_size=1024):
    """ Starting a TCP socket. """

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ADDR = (ip, port)
    """ Connecting to the server. """
    client.connect(ADDR)

    """ Sending either file """
    if filedir is not None:
        """ Opening and reading the file data. """
        size = os.path.getsize(filedir)
        sendPublicKey(client, keys)
        sendTransferParameters(client, keys, block_size, cipher_type, 0, size)
        cipher = None
        if cipher_type == 'cbc':
            print("[CLIENT]: Cipher type is CBC")
            cipher = Cipher(algorithms.AES(keys.session_key), modes.CBC(keys.iv))
        elif cipher_type == 'ecb':
            print("[CLIENT]: Cipher type is ECB")
            cipher = Cipher(algorithms.AES(keys.session_key), modes.ECB())
        """ Sending the filename to the server. """

        encrypted_filename = encrypt(bytes(os.path.basename(filedir),"utf-8"), cipher)

        print(f"CLIENT: Encryptedfilename {encrypted_filename}")
        client.send(encrypted_filename)
        msg = client.recv(SIZE).decode(FORMAT)
        print(f"[SERVER]: {msg}")

        """ Data transfer. """
        print("sending")
        bar = tqdm(range(size), f"Sending {filedir}", unit="B", unit_scale=True, unit_divisor=block_size)
        barprog["maximum"] = size
        barprog["value"] = 0
        with open(filedir, "rb") as f:
            while True:
                data = f.read(block_size)

                if not data:
                    break
                barprog["value"] += block_size
                win.update_idletasks()
                client.send(encrypt(data, cipher, barcyph, win))
                msg = client.recv(SIZE).decode(FORMAT)
                bar.update(len(data))
        barprog["value"] = size
        bar.update(len(data))

        """ Closing the connection """
        client.close()

def sendPublicKey(client, keys):
    """  Sending Public key of the user and receiving encrypted session key from the receiver """
    if keys.public_key is not None:
        client.send(keys.public_key.public_bytes(encoding=serialization.Encoding.PEM,
                                                format=serialization.PublicFormat.SubjectPublicKeyInfo))
        session_key_encrypted = client.recv(SIZE)
        keys.session_key = keys.private_key.decrypt(
                            session_key_encrypted,
                            padding.OAEP(
                                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                algorithm=hashes.SHA256(),
                                label=None
                            ))

        print(f"[CLIENT]: received session key {keys.session_key}")


def sendTransferParameters(client, keys, block_size, cipher_type, type_of_transfer, size):
    """ Sending transfer parameters to the receiver:
        <br/> client - receiving client
        <br/> keys - object of Keys class, containing session key.
        <br/> block_size - the size of one block of data transferred.
        <br/> cipher_type - either cbc or ecb.
        <br/> type_of_transfer - 0 for file transfer, 1 for text transfer
        <br/> size - total size of the file
        <br/> <br/> The parameters are serialized
        <br/> 5 bytes block size -- 3 bytes cipher type -- 1 byte for type -- 8 for size, i.e.:
        <br/> 10240cbc100016234
    """
    keys.iv = os.urandom(16)
    client.send(keys.iv)
    print(f"[CLIENT]  iv {keys.iv}")
    print(f"type_of_transfer {type_of_transfer}")
    parameters = bytes(str(block_size).zfill(8) + cipher_type + str(type_of_transfer) + str(size).zfill(8), "utf-8")
    print(f"[CLIENT] parameters {parameters}")

    padder = pd.PKCS7(128).padder()
    padded_data = padder.update(parameters) + padder.finalize()
    print(f"[CLIENT] padded = {padded_data}")

    cipher = Cipher(algorithms.AES(keys.session_key), modes.CBC(keys.iv))
    encryptor = cipher.encryptor()
    ct = encryptor.update(padded_data) + encryptor.finalize()
    print(f"[CLIENT] ct encrypted {ct}")

    client.send(ct)
