from gui import mainWindow
from network import server
from multiprocessing import Process

if __name__ == '__main__':
    p1 = Process(target=mainWindow.mainWindow())
    p1.start()
    p2 = Process(target=server.main)
    p2.start()
    p1.join()
    p2.join()
