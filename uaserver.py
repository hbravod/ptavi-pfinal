#!/usr/binver/python3
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from uaclient import XMLHandler
import os
import socket
import socketserver
import sys
import time


"""
def log(path, mensaje, evento):

    f = open(path, "a")
    if evento == 'Recieve':
        mensaje = time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(time.time())) +
                  ' Receive ' + mensaje.replace('\r\n', ' ') + '\r\n'
    if evento == 'Send':
        mensaje = time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(time.time())) +
                  ' Send ' + mensaje.replace('\r\n', ' ') + '\r\n'
    if evento == 'Error':
        mensaje = time.strftime('%Y-%m-%d %H:%M:%S',time.gmtime(time.time())) +
                 ' Error ' + message.replace('\r\n', ' ') + '\r\n'
    f.write(mensaje)
"""

class EchoHandler(socketserver.DatagramRequestHandler):
    """
    Echo server class
    """
    def error(self, line):
        line_errores = line.split(' ')
        fail = False
        if line_errores[1][0:4] != 'sip:':
            fail = True
        if line_errores[1].find('@') == -1:
            fail = True
        if line_errores[1].find(':') == -1:
            fail = True
        if line_errores[2] != 'SIP/2.0\r\n\r\n':
            fail = True
        return fail

    def handle(self):
        # Escribe dirección y puerto del cliente (de tupla client_address)

        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            mensaje = self.rfile.read().decode('utf-8')
            print('recibo cliente: ' + mensaje)
            lista = ['INVITE', 'ACK', 'BYE']
            method = mensaje.split()[0]
            if not mensaje:
                break

            if method not in lista:
                self.wfile.write(b"SIP/2.0 405 Method Not Allowed \r\n\r\n")

            elif self.error(mensaje):
                self.wfile.write(b"SIP/2.0 400 Bad Request \r\n\r\n")

            elif method == 'INVITE':
                self.wfile.write(bytes("SIP/2.0 100 Trying \r\n\r\n" +
                                       "SIP/2.0 180 Ringing \r\n\r\n" +
                                       "SIP/2.0 200 OK \r\n" + 
                                       'Content-Type: '+ 'application/sdp\r\n\r\n'
                                       + 'v=0\r\n' + 'o=' + USER + ' ' +
                                       str(IP_USER) + '\r\n' + 's=misesion\r\n' +
                                       't=0\r\n'+'m=audio' + ' ' + str(PORT_CANCION)
                                       + ' ' + 'RTP\r\n', 'utf-8'))

            elif method == lista[1]:
                print("ACK")          
                self.wfile.write(b"Recibido")
                aEjecutar = 'mp32rtp -i 127.0.0.1 -p 23032 < ' + sys.argv[3]
                print("Vamos a ejecutar", aEjecutar)
                os.system(aEjecutar)

            elif method == lista[2]:
                self.wfile.write(b"SIP/2.0 200 OK \r\n\r\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 uaserver.py config")

    CONFIG = sys.argv[1]
    XMLHandler.elparser()
    IP_PROXY = XMLHandler.dicc['regproxy_ip']
    PORT_PROXY = int(XMLHandler.dicc['regproxy_puerto'])
    IP_USER = XMLHandler.dicc['uaserver_ip']
    PORT_USER = int(XMLHandler.dicc['uaserver_puerto'])
    PORT_CANCION = int(XMLHandler.dicc['rtpaudio_puerto'])

    # Creamos servidor de eco y escuchamos
    SERV = socketserver.UDPServer((IP_USER, PORT_USER), EchoHandler)
    print("Listening...")
    try:
        SERV.serve_forever()
    except KeyboardInterrupt:
        print('Server Cancelled')
