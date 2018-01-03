#!/usr/binver/python3
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import os
import socketserver
import sys
import time


class PROXYHandler(ContentHandler):
    dicc = {}
    def __init__(self):

        self.labels = {'server': ['name', 'ip', 'puerto'],
                       'database': ['path', 'passwdpath'],
                       'log': ['path']
                      }

    def startElement(self, name, attrs):

        if name in self.labels:
            for atribute in self.labels[name]:
                self.dicc[name + "_" + atribute] = attrs.get(atribute, "")

    def get_tags(self):
        return(self.dicc)

    def elparser():
        parser = make_parser()
        cHandler = PROXYHandler()
        parser.setContentHandler(cHandler)
        parser.parse(open(sys.argv[1]))
        confdict = cHandler.get_tags()

class PROXYRegisterHandler(socketserver.DatagramRequestHandler):
    """
    Echo server class
    """
    dic_client = {}

    def BaseDatos(self, path):
        self.expired()
        f = open(path, "w")

        for usuario in self.dic_client:
            linea = (usuario + ' ' + self.dic_client[usuario][0] + ' ' +
                     str(self.dic_client[usuario][1]) + ' ' + 
                     self.dic_client[usuario][2] + ' ' +
                     self.dic_client[usuario][3] + '\r\n')
            f.write(linea)


    def expired(self):
        """
        Darse de baja en el servidor.
        """
        expirados = []
        time_act = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))
        for usuarios in self.dic_client:
            if self.dic_client[usuarios][3] < time_act:
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
                    print('register')
                    user = mensaje[1].split(':')[1]
                    direccion = self.client_address[0]
                    puerto = self.client_address[1]
                if mensaje[0] == 'Expires:':
                    if mensaje[1] != '0':
                        regist = time.strftime('%Y-%m-%d %H:%M:%S',
                                               time.gmtime(time.time()))
                        expire = time.strftime('%Y-%m-%d %H:%M:%S',
                                               time.gmtime(time.time() +
                                                           int(mensaje[1])))
                        self.dic_client[user] = [direccion, puerto, regist,
                                                 expire]
                        self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                    elif mensaje[1] == '0':
                        try:
                            del self.dic_client[user]
                            self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                        except KeyError:
                            self.wfile.write(b"SIP/2.0 404 USER"
                                             b"NOT FOUND\r\n\r\n")
                if mensaje[0] == 'INVITE':
                    print("invite")
   #            print(line.decode('utf-8'), end="")
        print(self.dic_client)
        self.BaseDatos(PATH_BASEDATOS)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 proxy_registrar.py config")

    PROXYHandler.elparser()

    ARCHIVO_XML = sys.argv[1]
    PORT_SERVER = int(PROXYHandler.dicc['server_puerto'])
    NAME_SERVER = PROXYHandler.dicc['server_name']
    IP_SERVER = PROXYHandler.dicc['server_ip']
    PATH_BASEDATOS = PROXYHandler.dicc['database_path']

    serv = socketserver.UDPServer(('', PORT_SERVER), PROXYRegisterHandler)
    print("Server MiServidorGuay listening at port 6003...")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print('Server Closed')
