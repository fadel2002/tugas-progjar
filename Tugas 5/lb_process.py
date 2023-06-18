from socket import *
import socket
import time
import sys
import logging
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from http import HttpServer

class BackendList:
	def __init__(self):
		self.servers=[]
		self.servers.append(('172.16.16.101',8887))
		self.servers.append(('172.16.16.104',9887))
		self.current=0
	def getserver(self):
		s = self.servers[self.current]
		self.current=self.current+1
		if (self.current>=len(self.servers)):
			self.current=0
		return s

def ProcessTheClient(connection,address,backend_sock,mode='toupstream'):
	while True:
		try:
			if (mode=='toupstream'):
				datafrom_client = connection.recv(32)
				if datafrom_client:
					backend_sock.sendall(datafrom_client)
				else:
					backend_sock.close()
					break
			elif (mode=='toclient'):
				datafrom_backend = backend_sock.recv(32)
				if datafrom_backend:
					connection.sendall(datafrom_backend)
				else:
					connection.close()
					break
		except OSError as e:
			pass
	connection.close()
	return

def Server(port=11001):
	the_clients = []
	my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	backend = BackendList()
	my_socket.bind(('', port))
	my_socket.listen(5)
	print(f"On port: {port}")

	with ProcessPoolExecutor(20) as executor:
		while True:
			connection, client_address = my_socket.accept()
			backend_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			backend_sock.settimeout(1)
			backend_address = backend.getserver()
			try:
				backend_sock.connect(backend_address)
				toupstream = executor.submit(ProcessTheClient, connection, client_address,backend_sock,'toupstream')
				toclient = executor.submit(ProcessTheClient, connection, client_address,backend_sock,'toclient')
			except Exception as err:
				pass

def main():
	Server(11001)

if __name__=="__main__":
	main()