import sys
import socket
import logging
import time
from multiprocessing import Process

def request():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # logging.warning("membuka socket")

    server_address = ('172.16.16.101', 45000)
    # logging.warning(f"opening socket {server_address}")
    sock.connect(server_address)

    try:
        # Send data
        message = 'TIME\r\n'
        logging.warning(f"[CLIENT] sending {message}")
        sock.sendall(message.encode('utf-8'))
        # Look for the response
        amount_received = 0
        amount_expected = len(message)
        while amount_received < amount_expected:
            data = sock.recv(1024).decode('utf-8')
            amount_received += len(data)
            logging.warning(f"[DITERIMA DARI SERVER] {data}")
    finally:
        # logging.warning("===================")
        # logging.warning("closing")
        # logging.warning("===================\n")
        sock.close()
    return


if __name__=='__main__':
    process = []
    for i in range(1000):
        proces = Process(target=request)
        process.append(proces)
        proces.start()
    for proces in process:
        proces.join()