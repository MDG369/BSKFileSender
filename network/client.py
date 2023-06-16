import os
import socket
from time import sleep

FORMAT = "utf-8"
SIZE = 1024

connected = False


def sendText(ip, port, text):
    """ Starting a TCP socket. """
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ADDR = (ip, port)
    """ Connecting to the server. """

    client.connect(ADDR)
    global connected
    connected = True
    sleep(1)
    """ 'TEXT' is appended to every text message to differentiate text and file transfer """
    if text is not None:
        client.send(b'TEXT' + bytes(text))

    """ Closing the connection from the server. """
    client.close()
    connected = False


def checkConnection():
    global connected
    print(connected)
    return connected


def sendFile(ip, port, filedir=None):
    """ Starting a TCP socket. """

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ADDR = (ip, port)
    """ Connecting to the server. """
    client.connect(ADDR)

    """ Sending either file """
    if filedir is not None:
        """ Opening and reading the file data. """
        file = open(filedir, 'r')
        data = file.read()

        """ Sending the filename to the server. """
        client.send(os.path.basename(filedir).encode(FORMAT))
        msg = client.recv(SIZE).decode(FORMAT)
        print(f"[SERVER]: {msg}")

        """ Sending the file data to the server. """
        client.send(data.encode(FORMAT))
        msg = client.recv(SIZE).decode(FORMAT)
        print(f"[SERVER]: {msg}")

        """ Closing the file. """
        file.close()
    """ Closing the connection from the server. """
    client.close()

