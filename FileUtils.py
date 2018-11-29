import os
import math
import hashlib

CHUNK_SIZE = 1480


class File():
    def __init__(self, name):
        self.name = name
        self.chunk_size = math.ceil(os.path.getsize(self.get_path()))
        self.reader = open(self.get_path(), 'rb')
        self.checksum = self.calculate_md5()

    def get_dict(self):
        dict = vars(self)
        del dict['reader']
        return dict

    def get_path(self):
        return './shared_files/' + self.name

    def calculate_md5(self):
        checksum = hashlib.md5(self.reader.read()).hexdigest()
        self.reader.seek(0)
        return checksum

    def get_chunk(self, offset):
        self.reader.seek(CHUNK_SIZE * offset)
        return self.reader.read(CHUNK_SIZE)


class Chunk():
    def __init__(self, offset):
        self.offset = offset
        self.data = None
        self.status = 'new'


class AvailableFile():
    def __init__(self, name, checksum, chunk_size, first_peer):
        self.name = name
        self.checksum = checksum
        self.chunk_size = chunk_size
        self.peers = [first_peer]
        self.status = 'discovered'

    def add_peer(self, ip):
        self.peers.append(ip)

    def start_download(self):
        self.chunks = [Chunk(i) for i in range(self.chunk_size)]
        self.status = 'downloading'

    def count_in_flight(self):
        return len([1 for chunk in self.chunks if chunk.status == 'in_flight'])

    def check_if_finished(self):
        return all(chunk.status == 'finished' for chunk in self.chunks)

    def get_batch_new_chunks(self, count=10):
        return [chunk for chunk in self.chunks if chunk.status == 'new'][:count]
