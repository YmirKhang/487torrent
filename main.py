import socket
import json
from FileUtils import AvailableFile, File, Chunk
import threading
import os

available_files = {}
shared_files = []

def initialize_files():
    for filename in os.listdir('shared_files/'):
        shared_files.append(File(filename))

def receive_file_definition(message):
    source, dict = message.split('|')
    file_list = json.loads(dict)
    for file in file_list:
        if file['checksum'] in available_files:
            available_files[file['checksum']].addPeer(source)
        else:
            available_files[file['checksum']] = AvailableFile (file['name'], file['checksum'], file['chunk_size'], source)

def send_discovery_request():
    pass

def receive_discovery():
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
                        #Handle message
                        conn.close()
                        break
                    message = message + data.decode('utf_8')

def listen_discovery(self):
    discovery_thread = threading.Thread(target=self.receive_discovery)
    discovery_thread.setDaemon(True)
    discovery_thread.start()





