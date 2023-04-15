import socket
IP = "localhost"
PORT = 15555

FORMAT = "utf-8"
SIZE = 1024


def send(ip, port):
    """ Staring a TCP socket. """

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ADDR = (ip, port)
    """ Connecting to the server. """
    client.connect(ADDR)

    """ Opening and reading the file data. """
    file = open("../data/file1.txt", "r")
    data = file.read()

    """ Sending the filename to the server. """
    client.send("file1.txt".encode(FORMAT))
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


if __name__ == "__main__":
    send(IP,PORT)