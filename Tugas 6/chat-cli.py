import socket
import os
import json
import sys
import logging

class ChatClient:
    def __init__(self, TARGET_IP, TARGET_PORT):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (TARGET_IP,TARGET_PORT)
        self.sock.connect(self.server_address)
        self.tokenid=""
        
    def proses(self,cmdline):
        j=cmdline.split(" ")
        try:
            command=j[0].strip()
            if (command=='auth'):
                username=j[1].strip()
                password=j[2].strip()
                return self.login(username,password)
            elif (command=='signup'):
                username=j[1].strip()
                password=j[2].strip()
                name=j[3].strip()
                country=j[4].strip()
                return self.signup(username, password, name, country)
            elif (command=='makegroup'):
                name_group = j[1].strip()
                password = j[2].strip()
                return self.makegroup(name_group, password)
            elif (command=='joingroup'):
                name_group = j[1].strip()
                password = j[2].strip()
                return self.joingroup(name_group, password)
            elif (command=='send'):
                usernameto = j[1].strip()
                message=""
                for w in j[2:]:
                   message="{} {}" . format(message,w)
                return self.sendmessage(usernameto,message)
            elif (command=='inbox'):
                return self.inbox()
            else:
                return "*Maaf, command tidak benar"
        except IndexError:
                return "-Maaf, command tidak benar"
            
    def sendstring(self,string):
        try:
            self.sock.sendall(string.encode())
            receivemsg = ""
            while True:
                data = self.sock.recv(64)
                # print(f"diterima dari server {data}")
                if (data):
                    receivemsg = "{}{}" . format(receivemsg,data.decode())  #data harus didecode agar dapat di operasikan dalam bentuk string
                    if receivemsg[-4:]=='\r\n\r\n':
                        print(f"diterima dari server {receivemsg}")
                        return json.loads(receivemsg)
        except:
            self.sock.close()
            return { 'status' : 'ERROR', 'message' : 'Gagal'}
        
    def login(self,username,password):
        string="auth\r\n{}\r\n{}\r\n\r\n" . format(username,password)
        result = self.sendstring(string)
        if result['status']=='OK':
            self.tokenid=result['tokenid']
            return "username {} logged in, token {} " .format(username,self.tokenid)
        else:
            return "Error, {}" . format(result['message'])
        
    def signup(self, username, password, name, country):
        string = f"signup\r\n{username}\r\n{password}\r\n{name}\r\n{country}\r\n\r\n"
        print(string)
        result = self.sendstring(string)
        if result['status']=='OK':
            return f"Berhasil buat email {result['email']}"
        else:
            return "Error, {}" . format(result['message'])
    
    def makegroup(self, name_group, password):
        if (self.tokenid==""):
            return "Error, not authorized"
        
        string = f"signup_group\r\n{self.tokenid}\r\n{name_group}\r\n{password}\r\n\r\n"
        print(string)
        result = self.sendstring(string)
        if result['status']=='OK':
            return f"email group {result['email_group']}"
        else:
            return "Error, {}" . format(result['message'])
    
    def joingroup(self, name_group, password):
        if (self.tokenid==""):
            return "Error, not authorized"
        
        string = f"signin_group\r\n{self.tokenid}\r\n{name_group}\r\n{password}\r\n\r\n"
        print(string)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "Berhasil join group"
        else:
            return "Error, {}" . format(result['message'])
        
    def sendmessage(self,usernameto="xxx",message="xxx"):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="send\r\n{}\r\n{}\r\n{}\r\n\r\n" . format(self.tokenid,usernameto,message)
        print(string)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "message sent to {}" . format(usernameto)
        else:
            return "Error, {}" . format(result['message'])
        
    def inbox(self):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="inbox\r\n{}\r\n\r\n" . format(self.tokenid)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "{}" . format(json.dumps(result['messages']))
        else:
            return "Error, {}" . format(result['message'])

        
def main():
    if (len(sys.argv) == 1):
        logging.error("Masukkan domain server pada command")
        return
    
    domain = sys.argv[1]
    TARGET_IP = ""
    if (domain == "domain1.com"):
        TARGET_IP = "172.16.16.101"
    elif(domain == "domain2.com"):
        TARGET_IP = "172.16.16.102"
    
    cc = ChatClient(TARGET_IP ,9001)
    while True:
        cmdline = input("Command {}:" . format(cc.tokenid))
        print(cc.proses(cmdline))

if __name__=="__main__":
    main()

