from tkinter import *
import socket
from network import client
from tkinter import filedialog as fd

file = ""
def chooseFileButton():
    global file
    file = fd.askopenfilename(initialdir='/')

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
    button_filedir_label = Label(text="Choose a file")
    button_filedir_label.pack()
    button_filedir = Button(window, text='Choose a file', command=lambda: chooseFileButton())
    button_filedir.pack()
    confirm = Button(window, text='Send', command=lambda: client.send(entry_ip.get(), int(entry_port.get()),
                                                                      file))
    confirm.pack()
    while True:
        window.update_idletasks()
        window.update()