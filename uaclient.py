#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Programa cliente que abre un socket a un servidor
"""
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import os
import socket
import sys


"""
def log(logfile, tipo, ip, mensaje):
    df = open(logfile, 'a')
"""
class XMLHandler(ContentHandler):
    dicc = {}
    def __init__(self):

        self.labels = {'account': ['username', 'psswd'],
                       'uaserver': ['ip', 'puerto'],
                       'rtpaudio': ['puerto'],
                       'regproxy': ['ip', 'puerto'],
                       'log': ['path'],
                       'audio': ['path']
                      }

    def startElement(self, name, attrs):

        if name in self.labels:
            for atribute in self.labels[name]:
                self.dicc[name + "_" + atribute] = attrs.get(atribute, "")

    def get_tags(self):
        return(self.dicc)

    def elparser():
        parser = make_parser()
        cHandler = XMLHandler()
        parser.setContentHandler(cHandler)
        parser.parse(open(CONFIG))
        confdict = cHandler.get_tags()

if __name__ == "__main__":
    CONFIG = sys.argv[1]
    METHOD = sys.argv[2]
    OPTION = sys.argv[3]

    if len(sys.argv) < 4:
        print("python3 uaclient.py config method option")

    XMLHandler.elparser()

    IP_uaserver = XMLHandler.dicc['regproxy_ip']
    PORT_uaserver = int(XMLHandler.dicc['regproxy_puerto'])
    USER = XMLHandler.dicc['account_username']
    PORT_CANCION = int(XMLHandler.dicc['rtpaudio_puerto'])

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        my_socket.connect((IP_uaserver, PORT_uaserver))

#        print("Enviando:", OPTION, USER, PORT_uaserver)
        if METHOD == "REGISTER":
            mensaje = ('REGISTER sip:'+USER+':'+str(PORT_uaserver)+ 
                       ' SIP/2.0\r\n\r\nExpires: ' +str(OPTION)+'\r\n')
            my_socket.send(bytes(mensaje, 'utf-8') + b'\r\n')
#            log(confdict['logfile'], 'sent', IP_uaserver, mensaje)
            print(mensaje)

        if METHOD == "INVITE":
            mensaje = ('INVITE sip:'+OPTION+' SIP/2.0\r\n'+'Content-Type: '+
                       'application/sdp\r\n'+'\r\n'+'v=0\r\n'+
                       'o='+USER+' '+str(IP_uaserver)+'\r\n'+'s=misesion\r\n'+
                       't=0\r\n'+'m=audio'+' '+str(PORT_CANCION)+' '+'RTP')
            my_socket.send(bytes(mensaje, 'utf-8') + b'\r\n')
            print(mensaje)

        if METHOD == "BYE":
            my_socket.send(bytes('BYE sip:'+USER+' SIP/2.0\r\n', 'utf-8') +
                           b'\r\n')
"""
    DATA = my_socket.recv(1024)

    print('Recibido -- ', data.decode('utf-8'))
    MESSAGE_RECIVIED = data.decode('utf-8').split(' ')
    for elementos in message_recivied:
        if method != "BYE" and elementos == '200':
            my_socket.send(bytes('ACK sip:' + LINE.split(':')[0] +
                                 ' SIP/2.0\r\n', 'utf-8') + b'\r\n')
    print("Terminando socket...")

    print("Fin.")
"""
