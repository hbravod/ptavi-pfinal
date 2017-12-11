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

CONFIG = sys.argv[1]
METHOD = sys.argv[2]
OPTION = sys.argv[3]

def log(logfile, tipo, ip, mensaje):
    df = open(logfile, 'a')

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

if __name__ == "__main__":

    if len(sys.argv) < 4:
        print("python3 uaclient.py config method option")

    parser = make_parser()
    cHandler = XMLHandler()
    parser.setContentHandler(cHandler)
    parser.parse(open(CONFIG))
    confdict = cHandler.get_tags()

    IP_uaserver = XMLHandler.dicc['uaserver_ip']
    PORT_uaserver = int(XMLHandler.dicc['uaserver_puerto'])
    USER = XMLHandler.dicc['account_username']

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        my_socket.connect((IP_uaserver, PORT_uaserver))

        print("Enviando:", OPTION)
        if METHOD == "REGISTER":
            mensaje = ('REGISTER sip:'+USER+' SIP/2.0\r\nExpires: ' +
                       OPTION+'\r\n', 'utf-8')
            my_socket.send(bytes(mensaje) + b'\r\n')
            log(confdict['logfile'], 'sent', IP_uaserver, mensaje)

        if METHOD == "INVITE":
            my_socket.send(bytes('INVITE sip:'+OPTION+' SIP/2.0\r\n', 'utf-8') +
                           b'\r\n')

        if METHOD == "BYE":
            my_socket.send(bytes('BYE sip:'+OPTION+' SIP/2.0\r\n', 'utf-8') +
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
