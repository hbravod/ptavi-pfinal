#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Programa cliente que abre un socket a un servidor
"""
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import hashlib
import os
import proxy_registrar
import socket
import sys
import time


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
        parser.parse(open(sys.argv[1]))
        confdict = cHandler.get_tags()

def checknonce(nonce):
    function_check = hashlib.md5()
    function_check.update(bytes(str(nonce), 'utf-8'))
    function_check.update(bytes(str(PASSWD), 'utf-8'))
    return function_check.hexdigest()

if __name__ == "__main__":

    if len(sys.argv) != 4:
        sys.exit("python3 uaclient.py config method option")

    CONFIG = sys.argv[1]
    METHOD = sys.argv[2]
    OPTION = sys.argv[3]

    XMLHandler.elparser()

    if XMLHandler.dicc['regproxy_ip'] == None:
        IP_PROXY = '127.0.0.1'
    else:
       IP_PROXY = XMLHandler.dicc['regproxy_ip']

    PORT_PROXY = int(XMLHandler.dicc['regproxy_puerto'])
    PORT_USER = int(XMLHandler.dicc['uaserver_puerto'])
    USER = XMLHandler.dicc['account_username']
    PORT_CANCION = int(XMLHandler.dicc['rtpaudio_puerto'])
    PASSWD = XMLHandler.dicc['account_psswd']

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        my_socket.connect((IP_PROXY, PORT_PROXY))

        if METHOD == "REGISTER":
            mensaje = (METHOD + ' sip:'+USER+':'+str(PORT_PROXY)+ 
                       ' SIP/2.0\r\n\r\nExpires: ' +str(OPTION)+'\r\n')
            my_socket.send(bytes(mensaje, 'utf-8') + b'\r\n')

            data = my_socket.recv(1024)
            message_recivied = data.decode('utf-8')
            if '401' in message_recivied:
                nonce = message_recivied.split('\r\n')[1].split()[3].split('"')[1]
                respuesta = checknonce(nonce)
                my_socket.send(bytes(METHOD + ' sip:' + USER + ":" + str(PORT_PROXY) +' SIP/2.0\r\n' + 'Expires: ' + str(OPTION) + '\r\n' + 'Authorization: Digest response="' + respuesta + '"', 'utf-8'))
            print(mensaje)

        if METHOD == "INVITE":
            mensaje = ('INVITE sip:'+OPTION+' SIP/2.0\r\n'+'Content-Type: '+
                       'application/sdp\r\n'+'\r\n'+'v=0\r\n'+
                       'o='+USER+' '+str(IP_PROXY)+'\r\n'+'s=misesion\r\n'+
                       't=0\r\n'+'m=audio'+' '+str(PORT_CANCION)+' '+'RTP')
            my_socket.send(bytes(mensaje, 'utf-8') + b'\r\n')
            print(mensaje)

        if METHOD == "BYE":
            my_socket.send(bytes('BYE sip:'+USER+' SIP/2.0\r\n', 'utf-8') +
                           b'\r\n')
        """
        data = my_socket.recv(1024)
        print('Recibido -- ', data.decode('utf-8'))
        message_recivied = data.decode('utf-8').split(' ')
        for elementos in message_recivied:
            if METHOD != "BYE" and elementos == '200':
                my_socket.send(bytes('ACK sip:' + ' SIP/2.0\r\n', 'utf-8') + b'\r\n')
        print("Terminando socket...")
        """
print("Fin.")
