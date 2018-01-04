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
    """
    def registrados(self, ARCHIVO_XML,):
        line = self.rfile.read()
        mensaje = line.decode('utf-8')
#        user = mensaje[0]   
#        puerto = mensaje[1]
#        expire = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time() +
#                               int(mensaje[1])))
        print(line.decode('utf-8'), end="")
        self.expired()
        self.BaseDatos(PATH_BASEDATOS)

        if usuario in self.dic_client:
            self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
        else:
            self.wfile.write(b"SIP/2.0 404 USER NOT FOUND\r\n\r\n")
    """


    def handle(self):
        """
        handle method of the server class
        (all requests will be handled by this method)
        """
        line = self.rfile.read()
        mensaje = line.decode('utf-8')
        metodo = mensaje.split()[0]
        usuario = mensaje.split()[1].split(':')[1]
        port = mensaje.split()[1].split(':')[2]
        expires = mensaje.split()[3]
        t_expires = mensaje.split()[4]
#        autor = mensaje.split()[5].split(':')[0]
        nonce = mensaje.split()[7].split('"')[1]
        nonce_num = '000000000'
        t_regist = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))
        t_expire = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time() +
                                 int(t_expires)))
        
        if mensaje:
            if metodo == 'REGISTER':
                direccion = self.client_address[0]
                puerto = self.client_address[1]
                if usuario in self.dic_client:
                    self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                else:
#                    if autor == 'Authorization':
#                       if nonce == nonce_num:
#                            self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
#                       self.dic_client[user] = [direccion, puerto, t_regist,
#                                             t_expire]
#                       self.BaseDatos(PATH_BASEDATOS)
#                    else:
#                       error = "SIP/2.0 401 Unauthorized" + '\r\n' + 
#                               "WWW Authenticate: Digest nonce=" + nonce_num
#                       self.wfile.write(b"error\r\n\r\n")

        print(line.decode('utf-8'), end="")
        print(self.dic_client)
        self.BaseDatos(PATH_BASEDATOS)
        self.registrados(ARCHIVO_XML)

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
