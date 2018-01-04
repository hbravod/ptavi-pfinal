#!/usr/binver/python3
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import hashlib
import os
import socketserver
import sys
import time
import random


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

    def passwd(user):
        with open(PATH_PSSWD, "r") as fichero:
            for linea in fichero:
                usuario_fichero = linea.split(' ')[1]
                if user == usuario_fichero:
                    passwd = line.split(' ')[3]
                    break
            return passwd

    def checknonce(nonce_user, user):
        function_check = hashlib.md5()
        function_check.update(bytes(nonce_user, 'utf-8'))
        function_check.update(bytes(passwd(user), 'utf-8'))
        function_check.digest()
        return function_check.hexdigest()

class PROXYRegisterHandler(socketserver.DatagramRequestHandler):
    """
    Echo server class
    """
    dic_client = {}
    dic_nonce = {}

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
        line = self.rfile.read()
        mensaje = line.decode('utf-8')
        metodo = mensaje.split()[0]
        usuario = mensaje.split()[1].split(':')[1]
        port = mensaje.split()[1].split(':')[2]
        t_expires = mensaje.split()[4]
        autor = mensaje.split('\r\n')[2].split(':')[0]
        
        if mensaje:
            if metodo == 'REGISTER':
                direccion = self.client_address[0]
                puerto = self.client_address[1]
                if usuario in self.dic_client:
                    if t_expires != '0':
                        t_expire = time.strftime('%Y-%m-%d %H:%M:%S', 
                                                 time.gmtime(time.time() + 
                                                 int(t_expires)))
                        self.dic_client[user][3] = t_expire
                        self.BaseDatos(PATH_BASEDATOS)
                        self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                    elif t_expires == '0':
                        del self.dic_client[user]
                        self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                else:
                    if autor == 'Authorization':
                       ua_response = mensaje.split('\r\n')[2].split('"')[1]
                       pr_response = checknonce(self.dic_nonce[usuario], usuario)
                       if ua_response == pr_response:
                           t_regist = time.strftime('%Y-%m-%d %H:%M:%S', 
                                                    time.gmtime(time.time()))
                           t_expire = time.strftime('%Y-%m-%d %H:%M:%S', 
                                                time.gmtime(time.time() + 
                                                int(t_expires)))
                           self.dic_client[user] = [direccion, puerto, 
                                                    t_regist, t_expire]
                           self.BaseDatos(PATH_BASEDATOS)
                           self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                       else:
                           error = "SIP/2.0 400 Bad Request"
                           self.wfile.write(b"error\r\n\r\n")
                    else:
                        nonce_num = random.randint(000000000, 999999999)
                        self.dic_nonce[usuario] = nonce_num
                        error = "SIP/2.0 401 Unauthorized\r\n" + 'WWW Authenticate: Digest nonce="' + str(self.dic_nonce[usuario]) + '"' + '\r\n\r\n'
                        self.wfile.write(bytes(error, 'utf-8'))

#            elif metodo == 'INVITE':
#            elif metodo == 'BYE':
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
    PATH_PSSWD = PROXYHandler.dicc['database_passwdpath']

    serv = socketserver.UDPServer(('', PORT_SERVER), PROXYRegisterHandler)
    print("Server MiServidorGuay listening at port 6003...")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print('Server Closed')
