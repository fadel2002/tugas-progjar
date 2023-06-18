import socket
import time
import sys
import logging
import multiprocessing
import concurrent.futures
import http

httpserver = http.HttpServer()

def ProcessTheClient(connection,address):
    received = ""
    while True:
        try:
            data = connection.recv(1024)
            if data:
                received = received + data.decode()
                if received[-4:]=='\r\n\r\n':
                    logging.warning("data dari client: {}" . format(received))
                    hasil = httpserver.proses(received)      
                    hasil = hasil + "\r\n\r\n".encode()
                    logging.warning("balas ke  client: {}" . format(hasil))
                    connection.sendall(hasil)
                    received = ""
                    connection.close()
                    break
            else:
                break
        except OSError as e:
            break
        except Exception as e:
            print(e)
    
    try:
        connection.shutdown(socket.SHUT_WR)
        connection.close()
    except:
        pass
    
    return

def Server(portnumber = 8887):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind(("0.0.0.0", portnumber))
    server_socket.listen(5)
    logging.warning("running on port {}" . format(portnumber))

    with concurrent.futures.ProcessPoolExecutor(20) as executor:
        while True:
            connection, client_address = server_socket.accept()
            executor.submit(ProcessTheClient, connection, client_address)

def main():
    portnumber=8887
    try:
        portnumber=int(sys.argv[1])
    except:
        pass
    Server(portnumber)

if __name__=="__main__":
    main()
