#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Programa cliente que abre un socket a un servidor
"""
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import socket
import sys

"""
if len(sys.argv) < 4:
    print("python3 uaclient.py config method option")

CONFIG = sys.argv[1]
METHOD = sys.argv[2]
OPTION = sys.argv[3]

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.connect((SERVER, PORT))

    if method == "INVITE":
        my_socket.send(bytes('INVITE sip:'+LINE+' SIP/2.0\r\n', 'utf-8') +
                       b'\r\n')

    if method == "BYE":
        my_socket.send(bytes('BYE sip:'+LINE+' SIP/2.0\r\n', 'utf-8') +
                       b'\r\n')

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
class XMLHandler(ContentHandler):

    def __init__(self):

        self.list = []
        self.labels = {'acount': ['username', 'psswd'],
                       'uaserver': ['ip', 'puerto'],
                       'rtpaudio': ['puerto'],
                       'regproxy': ['ip', 'puerto'],
                       'log': ['path'],
                       'audio': ['path']
                      }

    def startElement(self, name, attrs):

        diccionario = {}

        if name in self.labels:
            diccionario['name'] = name
            for atribute in self.labels[name]:
                diccionario[atribute] = attrs.get(atribute, "")
            self.list.append(diccionario)

    def get_tags(self):
        return(self.list)


if __name__ == "__main__":

    parser = make_parser()
    cHandler = XMLHandler()
    parser.setContentHandler(cHandler)
    parser.parse(open('ua1.xml'))
    print(cHandler.get_tags())
