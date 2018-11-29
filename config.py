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


SELF_IP = get_ip()
DISCOVERY_PORT = 5000
FILE_PORT = 5001
ACK_PORT = 5002
SUBNET = SELF_IP[:SELF_IP.rfind('.')]

MESSAGE_TYPES = {"request": 0, "response": 1}
