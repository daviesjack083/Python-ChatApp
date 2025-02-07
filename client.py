import socket
import json
import time
from datetime import datetime
from threading import Thread
from cryptography.fernet import Fernet
from commands import *


class Client():
    server_host = "127.0.0.1"
    server_port = 2745
    
    # Define socket
    s = socket.socket()
    buffer_size = 4096
    history = []

    # Encryption
    key = b'h05-DiFyVR460KNDlAwCmbHoaG-o0brFs_wwP8IX5xI='
    fernet = Fernet(key)


    def __init__(self):
        self.username = input("Enter a name to chat with: ")
        if len(self.username) < 1: self.username = "Undefined"

        # Open socket
        try:
            self.s.connect((self.server_host, self.server_port))
        except ConnectionRefusedError:
            print("Error: It appears that the server is down.")
            quit()

        self.speak(f"/name {self.username}")

        # Launch thread for listen
        t = Thread(target=self.listen)
        t.daemon = True
        t.start()

        # Enter chat mode
        message = ""
        while message != "q":
            self.refresh_screen()
            message = input()
            if len(message) < 1: continue

            # Broadcast
            self.speak(message)
        self.s.close()



    def listen(self):
        # Continuously loop and listen for new messages
        while True:
            try:
                message = self.s.recv(self.buffer_size)
                payload = self.fernet.decrypt(message)
                payload = json.loads(payload)
            
            except json.decoder.JSONDecodeError:
                self.history.append("Connection lost! Please restart the client!")
                return

            contents = f"{payload['sent']} - {payload['username']}: {payload['message']}"
            self.history.append(contents)
            self.refresh_screen()



    def speak(self, message):
        payload = {}
        payload['username'] = self.username.capitalize()
        payload['message'] = message
        payload['sent'] = datetime.fromtimestamp(time.time()).strftime("%H:%M:%S")

        if message[0] == "/":

            if message.split(' ')[0] == "/name":
                self.username = set_username(message)
                payload['username'] = self.username
            

        # Serialise, encrypt payload
        payload = json.dumps(payload)
        payload = self.fernet.encrypt(payload.encode())
        
        if len(payload) >= self.buffer_size:
            self.history.append(f"Message too long. Character limit: {self.buffer_size}")
            return

        self.s.send(payload)
        


    # As python does not have a bypass for the "\n" on input, redraw screen
    def refresh_screen(self):
        for i in range(500): print("\n")

        for message in self.history:
            print(message)




Client()
