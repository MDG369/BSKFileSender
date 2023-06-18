import multiprocessing
from ctypes import c_byte
from gui import MainWindow
from network import server
from multiprocessing import Process

if __name__ == '__main__':
    manager = multiprocessing.Manager()
    session_key = manager.Value(c_byte, "")

    p1 = Process(target=MainWindow.main)
    p1.start()
    p2 = Process(target=server.main)
    p2.start()
    p1.join()
    p2.join()
