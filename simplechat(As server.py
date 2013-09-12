#import socket module
import socket, threading

import pygtk
pygtk.require('2.0')
import gtk


PORT= 50080
BUFSIZE = 1024


class GUI:
    def destroy(self, widget, data=None):
        gtk.main_quit()
        
    def setAddress(self, widget):
        self.button5.hide()                       #hide address entry
        self.textbox1.hide()
        self.button6.show()                        #show port entry
        self.textbox2.show()
  
    def setPort(self, widget):
        self.button6.hide()                        #hide port entry
        self.textbox2.hide()
        self.button4.show()                        #show send entry
        self.textbox3.show()   
        clientMode()
        
    def getAddress(self):
        return self.textbox1.get_text()
        
    def getPort(self):
        return int(self.textbox2.get_text())
      
    def setClient(self, widget):
        self.window.set_title("myVPN-Client")
        self.button2.hide()
        self.button5.show()                         #show address entry
        self.textbox1.show()  
        
        
    def setServer(self, widget):                    #set as server side
        self.window.set_title("myVPN-Server")
        self.button1.hide()
        self.button4.show()                         #show send entry
        self.textbox3.show()  
        serverMode()
        
    def sendmessage(self, widget):
        self.label.set_text(self.textbox3.get_text()) 
        
    def displaymessage(self, message):
        self.label.set_text(self.message) 
        
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("destroy", self.destroy)  #close shell on gui close
        self.window.set_size_request(300,500)         #windows size
        self.window.set_title("myVPN")                #window title
        
        self.button1 = gtk.Button("Client")           #button1 Client Selection
        self.button1.connect("clicked", self.setClient) #what fn to call when clicked
        self.button2 = gtk.Button("Server")           #button2 Server Selection
        self.button2.connect("clicked", self.setServer)
        self.button3 = gtk.Button("Terminate")        #button3 terminate
        self.button3.connect("clicked", self.destroy)
        self.button4 = gtk.Button("Send")             #button4 send
        self.button4.connect("clicked", self.sendmessage)
        self.button5 = gtk.Button("Set Address")      #button5 Set Address
        self.button5.connect("clicked", self.setAddress)
        self.button6 = gtk.Button("Set Port")         #button6 Set Port
        self.button6.connect("clicked", self.setPort)
        self.textbox1 = gtk.Entry()                   #Address
        #self.textbox1.connect("changed", self.sendmessage)
        self.textbox2 = gtk.Entry()                   #Port
        #self.textbox1.connect("changed", self.sendmessage)
        self.textbox3 = gtk.Entry()                   #Msg to send
        #self.textbox1.connect("changed", self.sendmessage)
        
        self.hbox1=gtk.HBox()                          #Level 1, Client/Server Selection
        self.hbox1.pack_start(self.button1)
        self.hbox1.pack_start(self.button2)
        
        self.hbox2=gtk.HBox()                          #Level 2, blank on initialization
        self.hbox2.pack_start(self.textbox1)                #address
        self.hbox2.pack_start(self.button5)
        self.hbox2.pack_start(self.textbox2)                #port
        self.hbox2.pack_start(self.button6) 
        self.hbox2.pack_start(self.textbox3)                #msg
        self.hbox2.pack_start(self.button4)                 
        
        self.hbox3 = gtk.HBox()                       #Level 3, display msg
        self.frame = gtk.Frame("Chat Box")
        self.label = gtk.Label("Hello, Welcome to VPN")
        #label.set_justify(gtk.JUSTIFY_FILL)
        self.frame.add(self.label)
        self.hbox3.pack_start(self.frame, True, True, 0)
        
        self.hbox4=gtk.HBox()                         #Level 4, Termination
        self.hbox4.pack_start(self.button3)
        
        self.vbox1=gtk.VBox()                         #Put all hbox into vbox
        self.vbox1.pack_start(self.hbox1)
        self.vbox1.pack_start(self.hbox2)
        self.vbox1.pack_start(self.hbox3)
        self.vbox1.pack_start(self.hbox4)
        
        self.window.add(self.vbox1)                   #add vBox1 to window
        self.window.show_all()                        #display window
        
        self.button5.hide()                           #hide all level2 box first
        self.textbox1.hide()
        self.button6.hide()
        self.textbox2.hide()
        self.button4.hide()
        self.textbox3.hide()

    def main(self):
        gtk.main()

# handles data reception
class receiveHandler(threading.Thread):
    def __init__(self, sock):
        threading.Thread.__init__(self)
        self.sock = sock
        
    def run(self):
        while 1:
            try:
                # read message from the buffer
                data = self.sock.recv(BUFSIZE)
                if not data: 
                    # connection is closed
#                    print('read if not data')
                    break
                print(data)
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
    def __init__(self, sock):
        threading.Thread.__init__(self)
        self.sock = sock
        
    def run(self):
        while 1:
            # receive input
            data = raw_input(">>> ")
            if data == "quit": break
#            elif not data: continue
#            data = self.auth.encryptMsg(data)
#            print(data)
            try: self.sock.send(data)
            except:
#                print('send except') 
                break # error sending data
            
        try: self.sock.shutdown(socket.SHUT_RDWR) # on quit, send shutdown signal
        except: pass
        self.sock.close()

def serverMode():
    
    # Prepare a server socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', PORT))
    server.listen(1)
    
    while 1:    
        # Wait for the connection 
        print('Ready to serve...')
        conn, addr = server.accept()
                
        # start handler threads
        r = receiveHandler(conn)
        r.start()
        s = sendHandler(conn)
        s.start()
        
        # wait for the threads to finish
        s.join()
        r.join()
                    
    print('terminating server..')
    

def clientMode():
    # Prepare a client socket
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #addr = raw_input("Enter the target address: ")
    #port = raw_input("Enter the port number: ")
    addr = "localhost"
    port = "50080"
    #addr = gui.getAddress()
    #port = gui.getPort()
    
    print("Connecting to " + str(addr) + " " + str(port))
    
    # Connect to the server specified
    client.connect((addr,int(port)))
    raw_input("Press Enter") 
    print("Connected to " + str(addr) + " " + str(port))
    print("Enter \"quit\" to finish")
    
    # print(authen.encryptMsg("pppppp"))
    
    
    # start handler threads
    r = receiveHandler(client)
    r.start()
    s = sendHandler(client)
    s.start()
    
    # wait for the threads to finish
    s.join()
    r.join()

    print('terminating client..')
    
    client.close()
    
if __name__ == '__main__':
    # decide which mode it will run
    
    mode = raw_input("Which mode? (Server mode:1, Client mode:2) ")
    if mode == "1": serverMode()
    elif mode == "2": clientMode()
    else: 
        print("Wrong mode, terminating")
    
    
