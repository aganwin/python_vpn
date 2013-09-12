#!/usr/bin/env python


import pygtk
pygtk.require('2.0')
import gtk

class GUI:
    def destroy(self, widget, data=None):
        gtk.main_quit()
        
    def setAddress(self, widget):
        self.button5.hide()                     #hide address entry
        self.textbox1.hide()
        self.button6.show()                        #show port entry
        self.textbox2.show()
        
    def setPort(self, widget):
        self.button6.hide()                        #hide port entry
        self.textbox2.hide()
        self.button4.show()                        #show send entry
        self.textbox3.show()        
      
    def setClient(self, widget):
        self.window.set_title("myVPN-Client")
        self.button2.hide()
        self.button5.show()                        #show address entry
        self.textbox1.show()
        
        
    def setServer(self, widget):                    #set as server side
        self.window.set_title("myVPN-Server")
        self.button1.hide()
        self.button4.show()                         #show send entry
        self.textbox3.show()
        
    def sendmessage(self, widget):
        self.label.set_text(self.textbox3.get_text()) 
        
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
        self.label = gtk.Label("Hello")
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

        
#-----------------------------Code Begin-----------------------------        
if __name__ == "__main__":
    gui = GUI()
    gui.main()
    
