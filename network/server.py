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

        """ Bind the IP and PORT to the server. """
        server_socket.bind(ADDR)

        """ Server is listening, i.e., server is now waiting for the client to connected. """
        server_socket.listen()
        print("[LISTENING] Server is listening.")

        while True:
            """ Server has accepted the connection from the client. """
            conn, addr = server_socket.accept()
            print(f"[NEW CONNECTION] {addr} connected.")

            """ Receiving the either filename or text message from the client. """
            message = conn.recv(SIZE)

            # """ 'TEXT' is appended to every text message to differentiate text and file transfer """
            # if filename[:4] == 'TEXT':
            #     print(f"Received text message: {filename[4:]}")
            #     conn.send("Text message received".encode(FORMAT))

            print(f"{message}Received public key")
            self.keys.other_public_key = serialization.load_pem_public_key(message)
            conn.send(self.keys.generateSessionKey())

            print(f"[SERVER] sk = {self.keys.session_key}")

            self.keys.iv = conn.recv(SIZE)
            cipher = Cipher(algorithms.AES(self.keys.session_key), modes.CBC(self.keys.iv))
            session_parameters = decrypt(conn.recv(SIZE), cipher)
            block_size = int(session_parameters[:4])
            cipher_type = str(session_parameters[4:7])
            type_of_transfer = int(session_parameters[7:8])
            size = int(session_parameters[8:])
            print(f"{type_of_transfer} type of transfer {block_size} block size+ {cipher_type} size {size}")
            cipher = None
            if cipher_type == "b'cbc'" or cipher_type == b'cbc':
                print("SERVER CBC")
                cipher = Cipher(algorithms.AES(self.keys.session_key), modes.CBC(self.keys.iv))
            elif cipher_type == str(b'ecb') or cipher_type == b'ecb':
                print("SERVER ECB")
                cipher = Cipher(algorithms.AES(self.keys.session_key), modes.ECB())
            if type_of_transfer == 0:
                self.receiveFile(conn, block_size, cipher, size)
            elif type_of_transfer == 1:
                receiveText(conn)
            # else:
            #     print(f"[RECV] Receiving the filename.")
            #     file = open(filename, "w")
            #     conn.send("Filename received.".encode(FORMAT))
            #
            #     """ Receiving the file data from the client. """
            #     data = conn.recv(SIZE).decode(FORMAT)
            #     print(f"[RECV] Receiving the file data.")
            #     file.write(data)
            #     conn.send("File data received".encode(FORMAT))
            #
            #     """ Closing the file. """
            #     file.close()

            """ Closing the connection from the client. """
            conn.close()
            print(f"[DISCONNECTED] {addr} disconnected.")

    def receiveFile(self, conn, block_size, cipher, size):
        encrypted_filename = conn.recv(SIZE)
        print(f"SERVER: Encryptedfilename {encrypted_filename}")
        filename = decrypt(encrypted_filename, cipher)
        print(f"[+] Filename and filesize received from the client.{filename}")
        conn.send(f"{filename} Filename and filesize received".encode(FORMAT))

        """ Data transfer """
        bar = tqdm(range(size), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=self.block_size)

        with open(f"recv_{filename}", "w") as f:
            while True:
                data = conn.recv(block_size+32)

                if not data:
                    break

                f.write(decrypt(data, cipher).decode(FORMAT))
                conn.send("Data received.".encode(FORMAT))

                bar.update(len(data))


def receiveText(conn):
    pass


def decrypt(text, cipher):
    decryptor = cipher.decryptor()
    ct = decryptor.update(text) + decryptor.finalize()
    unpadder = pd.PKCS7(128).unpadder()
    unpadded_data = unpadder.update(ct) + unpadder.finalize()
    return unpadded_data


def main():
    server = Server()
    server.main()
