import socket

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as pd
from tqdm import tqdm

import security.KeyGeneration

IP = socket.gethostbyname(socket.gethostname())
PORT = 4455
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
SESSION_KEY_LOCATION = "keys/session_key/session_key.pem"


class Server:
    def __init__(self):
        self.keys = security.KeyGeneration.Keys()
        self.keys.readKeyPair(b'admin')
        self.block_size = SIZE
        self.cipher_type = "cbc"
        self.type_of_transfer = 0  # 0 is file, 1 is text
        self.size = 1

    def main(self):
        print("[STARTING] Server is starting.")
        """ Staring a TCP socket. """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        global PORT
        """ Bind the IP and PORT to the server. """
        while True:
            try:
                server_socket.bind((IP, PORT))
                break
            except OSError:
                PORT += 1

        """ Server is listening, i.e., server is now waiting for the client to connected. """
        server_socket.listen()
        print("[LISTENING] Server is listening.")

        while True:
            """ Server has accepted the connection from the client. """
            conn, addr = server_socket.accept()
            print(f"[NEW CONNECTION] {addr} connected.")

            """ Receiving the either filename or text message from the client. """
            message = conn.recv(SIZE)

            print(f"Received public key")
            self.keys.other_public_key = serialization.load_pem_public_key(message)
            conn.send(self.keys.generateSessionKey())

            print(f"[SERVER] session key = {self.keys.session_key}")

            self.keys.iv = conn.recv(SIZE)
            cipher = Cipher(algorithms.AES(self.keys.session_key), modes.CBC(self.keys.iv))
            session_parameters = decrypt(conn.recv(SIZE), cipher)
            block_size = int(session_parameters[:8])
            cipher_type = str(session_parameters[8:11])
            type_of_transfer = int(session_parameters[11:12])
            size = int(session_parameters[12:])
            cipher = None
            if cipher_type == "b'cbc'" or cipher_type == b'cbc':
                print("[SERVER] Cipher type is CBC")
                cipher = Cipher(algorithms.AES(self.keys.session_key), modes.CBC(self.keys.iv))
            elif cipher_type == str(b'ecb') or cipher_type == b'ecb':
                print("[SERVER] Cipher type is ECB")
                cipher = Cipher(algorithms.AES(self.keys.session_key), modes.ECB())
            print(type_of_transfer)
            if str(type_of_transfer) == '0':
                self.receiveFile(conn, block_size, cipher, size)
            elif str(type_of_transfer) == '1':
                receiveText(conn, cipher)
            """ Closing the connection from the client. """
            conn.close()
            print(f"[DISCONNECTED] {addr} disconnected.")

    def receiveFile(self, conn, block_size, cipher, size):
        encrypted_filename = conn.recv(SIZE)
        filename = decrypt(encrypted_filename, cipher)
        filename = filename.decode(FORMAT)
        print(f"[+] Filename and filesize received from the client.{filename}")
        conn.send(f"{filename} Filename and filesize received".encode(FORMAT))

        """ Data transfer """
        bar = tqdm(range(size), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=self.block_size)

        with open(f"recv_{filename}", "wb") as f:
            while True:
                data = conn.recv(block_size+32)

                if not data:
                    break

                f.write(decrypt(data, cipher))
                conn.send("Data received.".encode(FORMAT))

                bar.update(len(data))


def receiveText(conn, cipher):
    encrypted_message = conn.recv(SIZE)
    message = decrypt(encrypted_message, cipher)
    with open(f"recvmsg.txt", "ab") as f:
        f.write(message + b'\n')
    print(f"Received a message: {message}")


def decrypt(text, cipher):
    decryptor = cipher.decryptor()
    ct = decryptor.update(text) + decryptor.finalize()
    unpadder = pd.PKCS7(128).unpadder()
    unpadded_data = unpadder.update(ct) + unpadder.finalize()
    return unpadded_data


def main():
    server = Server()
    server.main()
