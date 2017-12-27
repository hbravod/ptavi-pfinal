#!/usr/binver/python3
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from uaclient import XMLHandler
import os
import socketserver
import sys


class EchoHandler(socketserver.DatagramRequestHandler):
    """
    Echo server class
    """
    def error(self, line):
        line_errores = line.split(' ')
        fail = False
        if len(line_errores) != 3:
            fail = True
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
            line = self.rfile.read()
            lista = ['INVITE', 'ACK', 'BYE']
            print('El cliente envía:' + line.decode('utf-8'))
            method = ((line.decode('utf-8')).split(' ')[0])
            if not line:
                break

            if method not in lista:
                self.wfile.write(b"SIP/2.0 405 Method Not Allowed \r\n\r\n")

            elif self.error(line.decode('utf-8')):
                self.wfile.write(b"SIP/2.0 400 Bad Request \r\n\r\n")

            elif method == lista[0]:
                self.wfile.write(b"SIP/2.0 100 Trying \r\n\r\n" +
                                 b"SIP/2.0 180 Ringing \r\n\r\n" +
                                 b"SIP/2.0 200 OK \r\n\r\n")

            elif method == lista[1]:
                aEjecutar = 'mp32rtp -i 127.0.0.1 -p 23032 < ' + sys.argv[3]
                aEjecutar += " < " + cancion.mp3
                print("Vamos a ejecutar", aEjecutar)
                os.system(aEjecutar)

            elif method == lista[2]:
                self.wfile.write(b"SIP/2.0 200 OK \r\n\r\n")


if __name__ == "__main__":
    CONFIG = sys.argv[1]
    XMLHandler.elparser()
    IP_uaserver = XMLHandler.dicc['uaserver_ip']
    PORT_uaserver = int(XMLHandler.dicc['uaserver_puerto'])
    if len(sys.argv) < 2:
        print("Usage: python3 uaserver.py config")

    # Creamos servidor de eco y escuchamos
    SERV = socketserver.UDPServer((IP_uaserver, PORT_uaserver), EchoHandler)
    print("Listening...")
    try:
        SERV.serve_forever()
    except KeyboardInterrupt:
        print('Server Cancelled')
