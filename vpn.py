#import socket module
import socket, threading
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random
from Crypto.Random import random

PORT= 50080
BUFSIZE = 4096

class auth():
    def conv(self, val, digit):
        return str(hex(val)).replace("0x","").replace("L","").zfill(digit)

    def generateClientKey(self):
        self.keyAB = self.conv(random.StrongRandom().getrandbits(128), 32)
        self.rA = self.conv(random.StrongRandom().getrandbits(128), 32)
        self.a = self.conv(random.StrongRandom().getrandbits(16), 4)
        h = SHA256.new()
        h.update('client'.encode('utf-8'))
        self.clienthash = h.hexdigest()
        return self.clienthash + self.keyAB + self.rA

    def generateServerKey(self, clientmsg):
        self.g = 6
        self.p = 15485863
        self.rB = self.conv(random.StrongRandom().getrandbits(128), 32)
        self.b = self.conv(random.StrongRandom().getrandbits(16), 4)
        h = SHA256.new()
        h.update('server'.encode('utf-8'))
        self.serverhash = h.hexdigest()
        self.clienthash = clientmsg[0:64]
        self.keyAB = clientmsg[64:96]
        self.rA = clientmsg[96:]   
    
    def encryptServerKey(self):
        msg = self.serverhash + str(self.rA) + str(self.g**int(self.b, 16) % self.p)
        iv = Random.new().read(AES.block_size)
        encryptor = AES.new(self.keyAB, AES.MODE_CFB, iv)
        cmsg = iv + str(self.rB) + str(self.g) + str(self.p) + encryptor.encrypt(msg)
        return cmsg
    
    def decryptServerKey(self, cmsg):
        iv = cmsg[0:16]
        self.rB = cmsg[16:48]
        self.g = int(cmsg[48:49])
        self.p = int(cmsg[49:57])
        ciphertext = cmsg[57:] 
        decryptor = AES.new(self.keyAB, AES.MODE_CFB, iv)
        plaintext = decryptor.decrypt(ciphertext)       
        serverhash = plaintext[0:64]
        rA = plaintext[64:96]
        gbp = plaintext[96:]
        if self.rA != rA: 
            print('rA incorrect')
            return False       
        h = SHA256.new()
        h.update('server'.encode('utf-8'))
        serverhash_orig = h.hexdigest()
        if serverhash_orig != serverhash: 
            print('server hash incorrect')
            return False      
        self.sessionKey = int(gbp)**int(self.a, 16) % self.p     
        return True 
    
    def encryptClientKey(self):
        msg = self.clienthash + str(self.rB) + str(self.g**int(self.a, 16) % self.p)
        iv = Random.new().read(AES.block_size)
        encryptor = AES.new(self.keyAB, AES.MODE_CFB, iv)
        cmsg = iv + encryptor.encrypt(msg)   
        return cmsg
    
    def decryptClientKey(self, cmsg):
        iv = cmsg[0:16]
        ciphertext = cmsg[16:]     
        decryptor = AES.new(self.keyAB, AES.MODE_CFB, iv)
        plaintext = decryptor.decrypt(ciphertext)    
        clienthash = plaintext[0:64]
        rB = plaintext[64:96]
        gap = plaintext[96:]   
        if self.rB != rB: 
            print('rB incorrect')
            return False     
        if self.clienthash != clienthash: 
            print('client hash incorrect')
            return False     
        self.sessionKey = int(gap)**int(self.b, 16) % self.p     
        return True
    
    def encryptMsg(self, msg):
        h = SHA256.new()
        h.update(str(self.sessionKey).encode('utf-8'))
        key = h.hexdigest()
        
        iv = Random.new().read(AES.block_size)
        encryptor = AES.new(key[0:32], AES.MODE_CFB, iv)
        cmsg = iv + encryptor.encrypt(msg)   
        return cmsg
    
    def decryptMsg(self, cmsg):
        iv = cmsg[0:16]
        ciphertext = cmsg[16:]
        
        h = SHA256.new()
        h.update(str(self.sessionKey).encode('utf-8'))
        key = h.hexdigest()
        
        decryptor = AES.new(key[0:32], AES.MODE_CFB, iv)
        plaintext = decryptor.decrypt(ciphertext)
    
        return plaintext


# handles data reception
class receiveHandler(threading.Thread):
    def __init__(self, sock, auth):
        threading.Thread.__init__(self)
        self.sock = sock
        self.auth = auth
        
    def run(self):
        while 1:
            try:
                # read message from the buffer
                data = self.sock.recv(BUFSIZE)
#                print(data)
                if not data: 
                    # connection is closed
#                    print('read if not data')
                    break
                plaindata = self.auth.decryptMsg(data)
#                print(data, len(data))
                print("(received) " + plaindata, "raw data: " + data)
            except: 
                # error occured
#                print('read except')
                break   
        
        print('Connection closed')
        try: self.sock.shutdown(socket.SHUT_RDWR)
        except: pass      
        self.sock.close()
        
# handles data transmission
class sendHandler(threading.Thread):
    def __init__(self, sock, auth):
        threading.Thread.__init__(self)
        self.sock = sock
        self.auth = auth
        
    def run(self):
        while 1:
            # receive input
            data = raw_input(">>> ")
            if data == "quit": break
#            elif not data: continue
            cipherdata = self.auth.encryptMsg(data)
#            print(data, len(data))
            try: self.sock.sendall(cipherdata)
            except:
#                print('send except') 
                break # error sending data
            
        try: self.sock.shutdown(socket.SHUT_RDWR) # on quit, send shutdown signal
        except: pass
        self.sock.close()

def serverMode(authmode):
    
    # Prepare a server socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', PORT))
    server.listen(1)
    
    if authmode == '2':
        # Manual session key
        sKey = raw_input("Please enter the session key: ")
    
    while 1:    
        # Wait for the connection 
        print('Ready to serve...')
        conn, addr = server.accept()
        
        if authmode == '1':
            # Session key generation
            authen = auth()
            data = conn.recv(BUFSIZE)
            authen.generateServerKey(data)
            data = authen.encryptServerKey()
            conn.send(data)
            data = conn.recv(BUFSIZE)
            authOK = authen.decryptClientKey(data)
            if authOK == False:
                print('Authentication failed')
                conn.shutdown(socket.SHUT_RDWR)
                conn.close
                continue
            elif authOK == True:
                print('Authentication successful')
                print('Session key =', authen.sessionKey)
        elif authmode == '2':
            authen = auth()
            authen.sessionKey = sKey
            
        print('Connection established', addr)
        
        # start handler threads
        r = receiveHandler(conn, authen)
        r.start()
        s = sendHandler(conn, authen)
        s.start()
        
        # wait for the threads to finish
        s.join()
        r.join()
                    
    print('terminating server..')
    server.close()

def clientMode(authmode):
    # Prepare a client socket
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    addr = raw_input("Enter the target address: ")
    port = raw_input("Enter the port number: ")
    if authmode == '2':
        sKey = raw_input("Please enter the session key: ")
        
    print("Connecting to " + str(addr) + " " + str(port))

    # Connect to the server specified
    client.connect((addr,int(port)))
    
    if authmode == '1':
        # Session key generation
        authen = auth()
        data = authen.generateClientKey()
        client.send(data)
        data = client.recv(BUFSIZE)
        authOK = authen.decryptServerKey(data)
        if authOK == False: 
            print('Authentication failed')
            client.shutdown(socket.SHUT_RDWR)
            client.close()
            return
        elif authOK == True:
            print('Authentication successful')
            print('Session key =', authen.sessionKey)
        
        data = authen.encryptClientKey()
        client.send(data)
    elif authmode == '2':
        authen = auth()
        authen.sessionKey = sKey
        
    print("Connected to " + str(addr) + " " + str(port))
    print("Enter \"quit\" to finish")

    # start handler threads
    r = receiveHandler(client, authen)
    r.start()
    s = sendHandler(client, authen)
    s.start()
    
    # wait for the threads to finish
    s.join()
    r.join()

    print('terminating client..')
    client.close()
    
if __name__ == '__main__':
    # decide which mode it will run
    mode = raw_input("Which mode? (Server mode:1, Client mode:2) ")
    authmode = raw_input("Automatic session key generation? (Auto:1, Manual:2) ")
    if mode == "1": serverMode(authmode)
    elif mode == "2": clientMode(authmode)
    else: 
        print("Wrong mode, terminating")
    
