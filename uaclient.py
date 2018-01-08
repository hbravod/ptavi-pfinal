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

        self.labels = {'account': ['username', 'passwd'],
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
    print('el nonce es: ' + str(nonce))
    function_check.update(bytes(str(PASSWD), 'utf-8'))
    print('la pass es: ' + str(PASSWD))
    print('cliente: ' + function_check.hexdigest())
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
    print('puerto user: ' + str(PORT_USER))
    USER = XMLHandler.dicc['account_username']
    PORT_CANCION = int(XMLHandler.dicc['rtpaudio_puerto'])
    PASSWD = XMLHandler.dicc['account_passwd']

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        my_socket.connect((IP_PROXY, PORT_PROXY))

        if METHOD == "REGISTER":
            mensaje = (METHOD + ' sip:'+USER+':'+str(PORT_USER)+ 
                       ' SIP/2.0\r\nExpires: ' +str(OPTION)+'\r\n')
            my_socket.send(bytes(mensaje, 'utf-8') + b'\r\n')

            data = my_socket.recv(1024)
            message_recivied = data.decode('utf-8')
            print('recibo del proxy: ' + message_recivied)
            if '401' in message_recivied:
                print(message_recivied)
                nonce = message_recivied.split('\r\n')[1].split()[3].split('"')[1]
                print(nonce)
                respuesta = checknonce(nonce)
                print('respuesta: ' + respuesta)
                my_socket.send(bytes(METHOD + ' sip:' + USER + ":" + str(PORT_USER) +' SIP/2.0\r\n' + 'Expires: ' + str(OPTION) + '\r\n' + 'Authorization: Digest response="' + respuesta + '"', 'utf-8'))
                my_socket.connect((IP_PROXY, PORT_PROXY))
                data = my_socket.recv(1024)
                message_recivied = data.decode('utf-8')
                print(message_recivied)
            print(mensaje)

        if METHOD == "INVITE":
            mensaje = (METHOD + ' sip:'+OPTION+' SIP/2.0\r\n'+'Content-Type: '+
                       'application/sdp\r\n'+'\r\n'+'v=0\r\n'+
                       'o='+USER+' '+str(PORT_USER)+'\r\n'+'s=misesion\r\n'+
                       't=0\r\n'+'m=audio'+' '+str(PORT_CANCION)+' '+'RTP')
            my_socket.send(bytes(mensaje, 'utf-8') + b'\r\n')
            print('mensaje que envia: ' + mensaje)

            data = my_socket.recv(1024)
            print('Recibido -- ' + data.decode('utf-8'))
            message_recivied = data.decode('utf-8').split()
            print('recibo del proxy: ' + str(message_recivied))

            if 'INVITE' in message_recivied:
                print('recibo del proxy: ' + data.decode('utf-8'))
                

            """

            envia = mensaje.split('\r\n')[4].split('=')[1].split()[0]
            print('envia: ' + envia)
            recibe = mensaje.split()[1].split(':')[1]
            print('recibe: ' + recibe)
            envia_ip = mensaje.split('\r\n')[4].split()[1]
            print('ip_envia: ' + envia_ip)
            my_socket.send(bytes(mensaje, 'utf-8') + b'\r\n')
            envia_port = mensaje.split('\r\n')[4].split('=')[1].split()[1]
            print('port_envia: ' + str(envia_port))
            print(mensaje)
            my_socket.connect((IP_PROXY, PORT_PROXY))

            data = my_socket.recv(1024)
            message_recivied = data.decode('utf-8')
            print('recibo del proxy: \r\n' + message_recivied)
            if message_recivied == 'ACK':
                print('me llega ack: ' + data.decode('utf-8'))
                my_socket.connect((envia_ip, envia_port))
                print('eyyy')
            """
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
