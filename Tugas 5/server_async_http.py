import socket
import time
import sys
import asyncore
import logging
from http import HttpServer

httpserver = HttpServer()
rcv = ""

class ProcessTheClient(asyncore.dispatcher_with_send):
	def handle_read(self):
		global rcv
		data = self.recv(1024)
		if data:
			d = data.decode()
			rcv = rcv + d
			if rcv[-4:] == '\r\n\r\n':
				logging.warning("data dari client: {}".format(rcv))
				hasil = httpserver.proses(rcv)
				hasil = hasil + "\r\n\r\n".encode()
				logging.warning("balas ke  client: {}".format(hasil))
				self.send(hasil)
				rcv = ""
				self.close()
		self.close()

class Server(asyncore.dispatcher):
	def __init__(self,portnumber):
		asyncore.dispatcher.__init__(self)
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.set_reuse_addr()
		self.bind(('',portnumber))
		self.listen(5)
		logging.warning("running on port {}" . format(portnumber))

	def handle_accept(self):
		pair = self.accept()
		if pair is not None:
			sock, addr = pair
			logging.warning("connection from {}" . format(repr(addr)))
			ProcessTheClient(sock)

def main():
	portnumber=8887
	try:
		portnumber=int(sys.argv[1])
	except:
		pass
	Server(portnumber)
	asyncore.loop()

if __name__=="__main__":
	main()

