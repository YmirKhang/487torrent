import threading
import os
import socket
import json
from FileUtils import File
from _thread import *
from config import *
from shutil import copyfile


class FileServer():
    def __init__(self):
        self.shared_files = []
        self.initialize_files()

    def start(self):
        self.broadcast_available_files()

    def initialize_files(self):
        for filename in os.listdir('shared_files/'):
            self.shared_files.append(File(filename))

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
