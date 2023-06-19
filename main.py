from gui import MainWindow, LoginWindow
from network import server
from multiprocessing import Process

if __name__ == '__main__':
    while True:
        if LoginWindow.loginWindow():
            p1 = Process(target=MainWindow.main)
            p1.start()
            p2 = Process(target=server.main)
            p2.start()
            p1.join()
            p2.join()
