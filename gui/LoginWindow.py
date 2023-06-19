import tkinter as tk
import security.KeyGeneration as key
password_correct = None


def loginWindow():
    window = tk.Tk()
    keys = key.Keys()
    greeting = tk.Label(window, text="Input the password")
    greeting.grid(row=0, column=0)
    password_entry = tk.Entry(window, show="*")
    password_entry.grid(row=1, column=0)
    button_confirm = tk.Button(window, text="Confirm", command=lambda: login(keys, password_entry.get(),
                                                                             password_label_text))
    button_confirm.grid(row=2, column=0)
    password_label_text = tk.StringVar(value='Input the password')
    password_label = tk.Label(window, textvariable=password_label_text)
    password_label.grid(row=3, column=0)
    while True:
        if password_correct:
            window.destroy()
            return True
        window.update_idletasks()
        window.update()


def login(keys, password, password_label_text):
    global password_correct
    try:
        keys.decryptPrivateKey(bytes(password, "utf-8"))
        password_correct = True
        print("Correct password")
    except ValueError:
        password_label_text.set("Password is wrong")
        print("Wrong password")
