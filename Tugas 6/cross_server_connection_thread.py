import sys
import os
import time
import logging
import threading
import json
import re
import socket
from cross_server import CrossServer
from queue import  Queue

MAPPING_SERVER_DOMAIN = {
    "domain1.com" : {"address" : ("172.16.16.101", 9000), "password" : "domain1" },
    "domain2.com" : {"address" : ("172.16.16.102", 9000), "password" : "domain2" },
    "domain3.com" : {"address" : ("172.16.16.103", 9000), "password" : "domain3" }
}

class BuatKoneksi(threading.Thread):
    def __init__(self, domain, cross_server, username, password):
        self.domain = domain
        self.cross_server = cross_server
        self.username = username
        self.password = password
        threading.Thread.__init__(self)
        
    def run(self):
        global MAPPING_SERVER_DOMAIN
        while(True):
            try:
                koneksi = self.cross_server.ambil_koneksi(self.domain)
                if (koneksi == False or koneksi["socket"] == None):
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    server_address = MAPPING_SERVER_DOMAIN[self.domain]["address"]
                    print("START")
                    sock.connect(server_address)
                    print("END")
                    sock.sendall(f"auth\r\n{self.username}\r\n{self.password}\r\n\r\n".encode())
                    hasil = ""
                    while True:
                        data = sock.recv(64)
                        if (data):
                            hasil += data.decode()
                        else:
                            break
                        if (hasil[-4:] == "\r\n\r\n"):
                            hasil_json = json.loads(hasil)
                            if (hasil_json["status"] == "OK"):
                                self.cross_server.set_koneksi(self.domain, sock, hasil_json["tokenid"])
                                logging.warning(f"CROSS SERVER: conected with domain : {self.domain}")
                            break
                    time.sleep(5)
                else:
                    time.sleep(10)
            except Exception as e:
                logging.warning(e)
                time.sleep(2)

class PenerimaPesan(threading.Thread):
    def __init__(self, connection, address, cross_server):
        self.connection = connection
        self.address = address
        self.cross_server = cross_server
        threading.Thread.__init__(self)

    def run(self):
        
        rcv=""
        while True:
            data = self.connection.recv(32)
            if data:
                d = data.decode()
                rcv=rcv+d
                if rcv[-4:]=='\r\n\r\n':
                    logging.warning("CROSS SERVER data delivered: {}" . format(rcv))
                    hasil = json.dumps(self.cross_server.proses(rcv))
                    hasil=hasil+"\r\n\r\n"
                    logging.warning("CROSS SERVER message {}" . format(hasil))
                    self.connection.sendall(hasil.encode())
                    rcv=""
            else:
                break
        self.connection.close()
        
class ChatNode(threading.Thread):
    def __init__(self, domain, cross_server):
        self.domain = domain
        self.queue_kotak_surat = Queue()
        self.socket_menuju_domain_lain = {}
        self.socket_dari_domain_lain = {}
        self.cross_server = cross_server
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        threading.Thread.__init__(self)

    def run(self):
        global MAPPING_SERVER_DOMAIN
        port = 9000
        self.my_socket.bind(('0.0.0.0',port))
        self.my_socket.listen(1)
        logging.warning("ChatNode PORT start at {}" . format(port))
        for domain in MAPPING_SERVER_DOMAIN:
            if (domain != self.domain):
                BuatKoneksi(domain, self.cross_server, self.domain, MAPPING_SERVER_DOMAIN[self.domain]["password"]).start()
        while True:
            self.connection, self.client_address = self.my_socket.accept()
            logging.warning("connection from {}" . format(self.client_address))
            PenerimaPesan(self.connection, self.client_address, self.cross_server).start()
            
if __name__=="__main__":
    ChatNode(sys.argv[1], CrossServer(sys.argv[1])).start()