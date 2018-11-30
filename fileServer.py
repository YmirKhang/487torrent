import threading
import os
import socket
import json
from FileUtils import File
from _thread import *
from config import *
from shutil import copyfile
import asyncio
import random


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

        is_new = source not in self.active_connections

        if is_new:
            loop = asyncio.get_running_loop()
            self.active_connections[source] = FileServerConnection(loop)

        file_connection = self.active_connections[source]

        for chunk in chunk_list:
            file_connection.add_chunk(file_hash, int(chunk), self.shared_files[file_hash].get_chunk(int(chunk)))
        if is_new:
            start_new_thread(asyncio.run, (self.start_connection(file_connection, source, loop),))

    async def start_connection(self, connection, source, loop):

        transport, protocol = await loop.create_datagram_endpoint(
            lambda: connection,
            remote_addr=(source, FILE_PORT))
        try:
            await protocol.on_con_lost
        finally:
            transport.close()

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
                            #conn.send(b"OK")
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

class SChunk:
    def __init__(self, file_hash, offset, data):
        self.offset = offset
        self.file_hash = file_hash
        self.data = data
        self.status = 'new'

    def get_key(self):
        return self.file_hash + "|" + str(self.offset)

    def get_bytes(self):
        return self.get_key().encode() + "|".encode() + self.data


class FileServerConnection:
    def __init__(self, loop):
        self.loop = loop
        self.transport = None
        self.window_size = TOLERANCE + 1
        self.in_flight = 0
        self.chunks = {}
        self.window_lock = threading.Lock()
        self.flight_lock = threading.Lock()
        self.on_con_lost = loop.create_future()
        self.started = False

    def set_window_size(self, value):
        self.window_lock.acquire()
        self.window_size = value
        self.window_lock.release()

    def inc_flight(self):
        self.flight_lock.acquire()
        self.in_flight += 1
        self.flight_lock.release()

    def dec_flight(self):
        self.flight_lock.acquire()
        self.in_flight -= 1
        self.flight_lock.release()

    def add_chunk(self, file_hash, offset, data):
        chunk = SChunk(file_hash, offset, data)
        self.chunks[chunk.get_key()] = chunk
        if self.started:
            asyncio.ensure_future(self.try_send(chunk, TRY_COUNT))

    def start(self):
        self.started = True
        for chunk in list(self.chunks.values()):
            asyncio.ensure_future(self.try_send(chunk, TRY_COUNT))

    async def probe(self):
        self.window_lock.acquire()
        if self.window_size <= TOLERANCE:
            print("Probing")
            self.transport.sendto("probe".encode())
        self.window_lock.release()
        await asyncio.sleep(1)
        await self.probe()

    async def try_send(self, chunk, count):
        if count == 0 or chunk.status == "done":
            self.chunks.pop(chunk.get_key(), None)
            self.check_if_complete()
            return

        if self.in_flight >= self.window_size - TOLERANCE:
            await asyncio.sleep(random.random())
            await self.try_send(chunk, count)
        else:
            #print("Try chunk #" + str(chunk) + " for " + str(self.try_count + 1 - count) + " times")
            chunk.status = "flight"
            self.inc_flight()
            self.transport.sendto(chunk.get_bytes())
            await asyncio.sleep(1)
            if chunk.status != "done":
                chunk.status = "new"
                self.dec_flight()
                await self.try_send(chunk, count - 1)

    def connection_made(self, transport):
        self.transport = transport
        self.start()
        asyncio.ensure_future(self.probe())

    def error_received(self, exc):
        print('Error received:', exc)

    def connection_lost(self, exc):
        print("Connection closed")
        self.on_con_lost.set_result(True)

    def check_if_complete(self):
        if not bool(self.chunks):
            print("Done")
            self.transport.close()

    def datagram_received(self, data, addr):
        message = data.decode()

        hash, chunk_num, window_size = message.split('|')
        self.set_window_size(int(window_size))

        if chunk_num == "-1":
            print("Probe returned")
            return

        self.chunks[hash + "|" + chunk_num].status = "done"
        self.chunks.pop(hash + "|" + chunk_num, None)
        self.dec_flight()
        self.check_if_complete()


