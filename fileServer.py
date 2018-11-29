import threading
import os
import socket
import json
from FileUtils import File
from _thread import *
from config import *
from shutil import copyfile

class FileServer:

    def __init__(self):
        self.shared_files = {}
        self.active_connections = {}
        self.initialize_files()

    def start(self):
        self.broadcast_available_files()

    def initialize_files(self):
        for filename in os.listdir('shared_files/'):
            file = File(filename)
            self.shared_files[file.checksum] = file

    def handle_chunk_request(self, message):
        source, file_hash, raw_chunks = message.split('|')
        chunk_list = json.loads(raw_chunks)
        if source not in self.active_connections:
            self.active_connections[source] = FileServerConnection() # TODO

        file_connection = self.active_connections[source]

        for chunk in chunk_list:
            file_connection.add_chunk(file_hash, int(chunk), self.shared_files[file_hash].get_chunk(int(chunk)))

        file_connection.start()

    def receive_chunk_request(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((SELF_IP, CHUNK_PORT))
            s.listen()

            while True:
                conn, addr = s.accept()
                with conn:
                    message = ""
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            self.handle_chunk_request(message)
                            conn.send(b"OK")
                            conn.close()
                            break
                        message = message + data.decode('utf_8')


    def listen_chunk_request(self):
        chunk_thread = threading.Thread(target=self.receive_chunk_request)
        chunk_thread.setDaemon(True)
        chunk_thread.start()

    def add_file(self, filepath):
        if os.path.isfile(filepath):
            copyfile(filepath, 'shared_files/')
            self.shared_files.append(File(os.path.basename(filepath)))
            self.broadcast_available_files()
            print("File added successfully: " + os.path.basename(filepath))
        else:
            print("Not a valid file")

    def broadcast_available_files(self):
        for i in range(1, 255):
            target_ip = SUBNET + "." + str(i)
            if target_ip != SELF_IP:
                self.send_available_files(target_ip, MESSAGE_TYPES['request'])

    def send_available_files(self, target_ip, type):
        message = SELF_IP + "|" + type + "|" + json.dumps([data.get_dict() for data in self.shared_files])
        start_new_thread(self.send_packet, (target_ip, DISCOVERY_PORT, message,))

    def send_packet(self, host, port, message):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect((host, port))
                s.send(message.encode('utf-8'))
                s.close()
        except:
            print("Error while sending packet: " + message)


class FileServerConnection:
    def __init__(self):
        pass

    def add_chunk(self, file_hash, offset, data):
        pass

    def start(self):
        pass
