import socket
import json
from FileUtils import AvailableFile, File, Chunk
import threading
import os
from config import *


class FileClient():
    def __init__(self, send_file_callback):
        self.available_files = {}
        self.send_file_callback = send_file_callback

    def handle_file_definition(self, message):
        source, type, dict = message.split('|')
        file_list = json.loads(dict)
        for file in file_list:
            if file['checksum'] in self.available_files:
                self.available_files[file['checksum']].addPeer(source)
            else:
                self.available_files[file['checksum']] = AvailableFile(file['name'], file['checksum'],
                                                                       file['chunk_size'], source)
        if type == MESSAGE_TYPES["request"]:
            self.send_file_callback(source, MESSAGE_TYPES["response"])

    def receive_discovery(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((SELF_IP, DISCOVERY_PORT))
            s.listen()

            while True:
                conn, addr = s.accept()
                with conn:
                    message = ""
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            self.handle_file_definition(message)
                            conn.close()
                            break
                        message = message + data.decode('utf_8')


    def listen_discovery(self):
        discovery_thread = threading.Thread(target=self.receive_discovery)
        discovery_thread.setDaemon(True)
        discovery_thread.start()
