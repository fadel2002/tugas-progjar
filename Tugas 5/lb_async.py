import socket
import time
import sys
import asyncore
import logging


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


class Backend(asyncore.dispatcher_with_send):
	def __init__(self,targetaddress):
		asyncore.dispatcher_with_send.__init__(self)
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connect(targetaddress)
		self.connection = self

	def handle_read(self):
		try:
			self.client_socket.send(self.recv(32))
		except:
			pass
	def handle_close(self):
		try:
			self.close()
			self.client_socket.close()
		except:
			pass


class ProcessTheClient(asyncore.dispatcher):
	def handle_read(self):
		data = self.recv(32)
		if data:
			self.backend.client_socket = self
			self.backend.send(data)
	def handle_close(self):
		self.close()

class Server(asyncore.dispatcher):
	def __init__(self,portnumber):
		asyncore.dispatcher.__init__(self)
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.set_reuse_addr()
		print(f"On port: {portnumber}")
		self.bind(('',portnumber))
		self.listen(5)
		self.bservers = BackendList()

	def handle_accept(self):
		pair = self.accept()
		if pair is not None:
			sock, addr = pair
			bs = self.bservers.getserver()
			backend = Backend(bs)
			handler = ProcessTheClient(sock)
			handler.backend = backend


def main():
	portnumber=11001
	try:
		portnumber=int(sys.argv[1])
	except:
		pass
	svr = Server(portnumber)
	asyncore.loop()

if __name__=="__main__":
	main()
