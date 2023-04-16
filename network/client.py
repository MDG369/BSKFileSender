import os
import socket
FORMAT = "utf-8"
SIZE = 1024


def send(ip, port, filedir):
    """ Staring a TCP socket. """

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ADDR = (ip, port)
    """ Connecting to the server. """
    client.connect(ADDR)

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
