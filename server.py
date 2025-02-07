import socket
import json
import time
import cryptography
from datetime import datetime
from threading import Thread
from cryptography.fernet import Fernet


class Server():
    server_host = '192.168.0.25'
    server_port = 6441

    # Socket
    clients = set()
    buffer_size = 4096
    
    # Encryption
    key = b'h05-DiFyVR460KNDlAwCmbHoaG-o0brFs_wwP8IX5xI='
    fernet = Fernet(key)

    def __init__(self):
        # Configure socket
        self.s = socket.socket()
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((self.server_host, self.server_port))
        self.s.listen(5)

        # Server running
        print(f"Server Listening on: {self.server_host}:{self.server_port}")
        while True:
            client_socket, client_address = self.s.accept()
            self.clients.add(client_socket)
            print(f"{client_address} connected. Active Clients: {len(self.clients)}")
            self.announce(self.clients, f"{client_address} has entered the temple.")

            # Open thread
            t = Thread(target=self.listen, args=(client_socket,))
            t.daemon = True
            t.start()



    def listen(self, cs):
        username = ""
        while True:

            try:
                message = cs.recv(self.buffer_size)
                #decode = self.fernet.decrypt(message)
                decode = json.loads(message)
            
            except (ConnectionResetError):
                print(f"{cs.getpeername()} ({username}) disconnected. Active Clients: {len(self.clients)}")
                self.clients.remove(cs)
                return  
            
            except (cryptography.fernet.InvalidToken):
                decode = json.loads(message)

            except (TypeError, json.decoder.JSONDecodeError):
                print(f"{cs.getpeername()} ({username}) disconnected. Active Clients: {len(self.clients)}")
                self.clients.remove(cs)
                return              
            
            ip = cs.getpeername()

            if decode['message'].split(' ')[0] == "/name":
                self.announce(self.clients, f"{ip} {username} is now known as {decode['username']}!")
                username = decode['username']
            else:
                print(f"{decode['sent']} - {decode['username']}: '{decode['message']}' | {ip}")
                for client_socket in self.clients:
                    client_socket.send(message)
                

            
    def announce(self, socket, message):
        payload = {}
        payload['username'] = "[*]Server"
        payload['message'] = message
        payload['sent'] = datetime.fromtimestamp(time.time()).strftime("%H:%M:%S")

        payload = json.dumps(payload)
        #payload = self.fernet.encrypt(payload.encode())

        print("Announced: " + payload)

        if "socket" in str(type(socket)):
            socket.send(payload.encode())
        else:
            for client in socket:
                client.send(payload.encode())



Server()