import re
import random
import socket
from time import time


def query(host, port):
    if host in ["127.0.0.1", "0.0.0.0", "192.168.0.1", "192.168.1.0"] or host.lower() == "localhost":
        return {'error': 'Сервер не отвечает'}

    start_time = time()
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1)
    except socket.error as err:
        return {'error': str(err)}

    rand_int = random.randint(1, 999999999)
    req_packet = b"\x01"
    req_packet += rand_int.to_bytes(8, byteorder="big")
    req_packet += b"\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x12\x34\x56\x78"  # magic string
    req_packet += (0).to_bytes(8, byteorder="big")

    try:
        sock.sendto(req_packet, (host, port))
        response, _ = sock.recvfrom(4096)
    except socket.timeout:
        return {'error': 'Сервер не отвечает'}
    finally:
        sock.close()

    if not response or response[0] != 0x1C:
        return {'error': 'Ошибка обработки'}

    server_info = response[35:].decode()
    server_info = re.sub("#ยง.", "", server_info)
    server_info = server_info.split(";")

    end_time = time()
    execution_time = (end_time - start_time) * 1000

    return {
        'error': "Успех",
        'time': execution_time,
        'motd': server_info[1],
        'num': server_info[4],
        'max': server_info[5],
        'version': server_info[3],
    }


