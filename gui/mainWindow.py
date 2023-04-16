from tkinter import *
import socket
from network import client
def mainWindow():
    window = Tk()
    window.title("BSKFileSender")
    window.geometry("300x300")
    user_ip_label = Label(text="Your IP")
    user_ip_label.pack()
    t = Label(text=socket.gethostbyname(socket.gethostname()))
    t.pack()
    entry_ip_label = Label(text="Receiver IP")
    entry_ip_label.pack()
    entry_ip = Entry(window)
    entry_ip.pack()
    entry_port_label = Label(text="Receiver Port")
    entry_port_label.pack()
    entry_port = Entry(window)
    entry_port.pack()
    confirm = Button(window, text='Send', command=lambda: client.send(entry_ip.get(), int(entry_port.get())))
    confirm.pack()
    while True:
        window.update_idletasks()
        window.update()