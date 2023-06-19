import os
import tkinter as tk
import socket
from tkinter.constants import HORIZONTAL
from tkinter.ttk import Progressbar

from cryptography.hazmat.primitives import serialization

from network import client
from tkinter import filedialog as fd
import security.KeyGeneration
file = ""

class TkinterApp(tk.Tk):

    # __init__ function for class tkinterApp
    def __init__(self, *args, **kwargs):
        # __init__ function for class Tk
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("BSKTransfer")
        # creating a container
        container = tk.Frame(self)
        container.grid(row=0, column=0)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.geometry("600x400")
        # initializing frames to an empty array
        self.frames = {}

        # iterating through a tuple consisting
        # of the different page layouts
        for F in (MainWindow,TextWindow):
            frame = F(container, self)

            # initializing frame of that object from
            # startpage, page1, page2 respectively with
            # for loop
            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(MainWindow)



    # to display the current frame passed as
    # parameter
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class MainWindow(tk.Frame):
    def __init__(self, parent, controller):
        self.keys = security.KeyGeneration.Keys()
        self.keys.readKeyPair(password=b'admin')
        tk.Frame.__init__(self, parent)

        button1 = tk.Button(self, text="Text communicator",
                            command=lambda: controller.show_frame(TextWindow))
        button1.grid(row=0, column=6, padx=10, pady=2)

        entry_ip, entry_port = self.createIpPortSelection()
        mode = tk.StringVar(value='cbc')
        button_ciphermode = tk.Button(self, textvariable=mode, command=lambda: self.switchCipherMode(mode))
        button_ciphermode.grid(row=3, column=2, ipadx=5, pady=2)
        button_filedir = tk.Button(self, text='Choose a file', command=lambda: self.chooseFileButton())
        button_filedir.grid(row=3, column=1, ipadx=5, pady=2)

        bar = Progressbar(self, orient=HORIZONTAL, length=300)
        bar.grid(row=5, column=1, ipadx=5, padx=10, pady=2)
        confirm = tk.Button(self, text='Send', command=lambda: client.sendFile(entry_ip.get(), int(entry_port.get()),
                                                                               self, bar, self.keys, file, mode.get()))
        confirm.grid(row=4, column=1, ipadx=5, padx=10, pady=2)

    @staticmethod
    def chooseFileButton():
        global file
        file = fd.askopenfilename(initialdir='/')

    @staticmethod
    def switchCipherMode(mode):
        if mode.get() == 'cbc':
            mode.set('ecb')
        else:
            mode.set('cbc')

    def establishConnection(self, entry_ip, entry_port):
        client.sendPublicKey(entry_ip.get(), int(entry_port.get()),
                             self.keys)




    def createIpPortSelection(self):
        """ This function creates labels and entries for setting transfer receiver, as well as a label displaying
         users ip address """

        user_ip_label = tk.Label(self, text="Your IP")
        user_ip_label.grid(row=0, column=0, padx=10, pady=2)
        t = tk.Label(self, text=socket.gethostbyname(socket.gethostname()))
        t.grid(row=0, column=1, pady=2)

        entry_ip_label = tk.Label(self, text="Receiver IP")
        entry_ip_label.grid(row=1, column=0, padx=10, pady=2)

        entry_ip = tk.Entry(self)
        entry_ip.grid(row=1, column=1, pady=2)
        entry_ip.insert(0, socket.gethostbyname(socket.gethostname()))

        entry_port_label = tk.Label(self, text="Receiver Port")
        entry_port_label.grid(row=2, column=0, padx=10, pady=2)

        entry_port = tk.Entry(self)
        entry_port.grid(row=2, column=1, pady=2)
        entry_port.insert(0, "4455")

        return entry_ip, entry_port


class TextWindow(MainWindow):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.keys = security.KeyGeneration.Keys()
        self.keys.readKeyPair(password=b'admin')
        button1 = tk.Button(self, text="File transfer",
                            command=lambda: controller.show_frame(MainWindow))
        button1.grid(row=0, column=6, padx=10, pady=2, ipadx=20)
        conn_message_label = tk.Label(self, textvariable="True")
        conn_message_label.grid(row=3, column=2, padx=10, pady=2)
        entry_ip, entry_port = self.createIpPortSelection()

        text_message_label = tk.Label(self, text="Message")
        text_message_label.grid(row=3, column=0, padx=10, pady=2)
        entry_text_message = tk.Entry(self)
        entry_text_message.grid(row=3, column=1, pady=2)
        msg = tk.StringVar(value='No message received')
        message_label = tk.Label(self, textvariable=msg)
        message_label.grid(row=8, column=1)
        button_read_message = tk.Button(self, text='Read a message', command=lambda: self.readMessage(msg))
        button_read_message.grid(row=7, column=1)

        confirm = tk.Button(self, text='Send', command=lambda: client.sendText(entry_ip.get(), int(entry_port.get()),self.keys,
                                                                               bytes(entry_text_message.get(), "utf-8")))
        confirm.grid(row=4, column=1, ipadx=5, padx=10, pady=2)

    def updateDisplay(self, myString, displayVar):
        displayVar.set(myString)

    @staticmethod
    def readMessage(msg):
        try:
            f = open("recvmsg.txt", "r")
            msg.set(f.read())
            f.close()
            os.remove("recvmsg.txt")
        except FileNotFoundError:
            msg.set("No messages received")


def main():
    app = TkinterApp()
    while(True):

        app.mainloop()

