from tkinter import *
import socket
import client
import server
from multiprocessing import Process
def mainwindow():
    window = Tk()
    window.title("BSKFileSender")
    window.geometry("300x300")
    input_label = Label(text="Receiver IP")
    input_label.pack()
    t = Label(text=socket.gethostbyname(socket.gethostname()))
    t.pack()
    entry_ip = Entry(window)
    entry_ip.pack()
    entry_port = Entry(window)
    entry_port.pack()
    confirm = Button(window, text='submit', command=lambda: client.send(entry_ip.get(), int(entry_port.get())))
    confirm.pack()
    while True:
        window.update_idletasks()
        window.update()

if __name__ == '__main__':
    p1 = Process(target=mainwindow)
    p1.start()
    p2 = Process(target=server.main)
    p2.start()
    p1.join()
    p2.join()

