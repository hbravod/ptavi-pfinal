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
import time


class SIPRegisterHandler(socketserver.DatagramRequestHandler):
    """
    Echo server class
    """
    dic_client = {}

    def expired(self):
        """
        Darse de baja en el servidor.
        """
        expirados = []
        time_act = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))
        for usuarios in self.dic_client:
            if self.dic_client[usuarios][1] < time_act:
                expirados.append(usuarios)
        for usuarios in expirados:
            del self.dic_client[usuarios]

    def handle(self):
        """
        handle method of the server class
        (all requests will be handled by this method)
        """
        for line in self.rfile:
            mensaje = line.decode('utf-8').split()
            if mensaje:
                if mensaje[0] == 'REGISTER':
                    user = mensaje[1][4:]
                    direccion = self.client_address[0]
                if mensaje[0] == 'Expires:':
                    if mensaje[1] != '0':
                        expire = time.strftime('%Y-%m-%d %H:%M:%S',
                                               time.gmtime(time.time() +
                                                           int(mensaje[1])))
                        self.dic_client[user] = [direccion, expire]
                        self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                    elif mensaje[1] == '0':
                        try:
                            del self.dic_client[user]
                            self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                        except KeyError:
                            self.wfile.write(b"SIP/2.0 404 USER"
                                             b"NOT FOUND\r\n\r\n")
            print(line.decode('utf-8'), end="")
        print(self.dic_client)

if __name__ == "__main__":
    PORT = int(sys.argv[1])
    XMLHandler.elparser()
    if len(sys.argv) < 2:
        print("Usage: python3 proxy_registrar.py config")
    serv = socketserver.UDPServer(('', PORT), SIPRegisterHandler)
    print("Server MiServidorGuay listening at port 5555...")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print('Server Cancelled')
