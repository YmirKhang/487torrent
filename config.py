import socket


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


FILE_PATH = './shared_files/'
SELF_IP = get_ip()
DISCOVERY_PORT = 5000  # TCP
CHUNK_PORT = 5001  # TCP
FILE_PORT = 5001  # UDP
ACK_PORT = 5001  # UDP

DEFAULT_WINDOW_SIZE = 100
TRY_COUNT = 5
TOLERANCE = 3
DRAINAGE = 0.05

SUBNET = SELF_IP[:SELF_IP.rfind('.')]

MESSAGE_TYPES = {"request": 0, "response": 1}
