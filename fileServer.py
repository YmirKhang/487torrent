import threading
import os
import socket
from FileUtils import File
from _thread import *
from config import *
from shutil import copyfile

class FileServer():
    def __init__(self):
        self.shared_files = []
        self.initialize_files()

    def initialize_files(self):
        for filename in os.listdir('shared_files/'):
            self.shared_files.append(File(filename))

    def add_file(self, filepath):
        if os.path.isfile(filepath):
            copyfile(filepath,'shared_files/')
            self.shared_files.append(File(os.path.basename(filepath)))
            return True
        else:
            print("Not a valid file")
            return False

def inform_network(self):
    for i in range(1, 255):
        target_ip = SUBNET + "." + str(i)
        if target_ip != SELF_IP:
            message = ""
        start_new_thread(self.send_packet, (target_ip, DISCOVERY_PORT, message,))


def send_packet(self, host, port, message):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.connect((host, port))
            s.send(message.encode('utf-8'))
            s.close()
    except:
        pass