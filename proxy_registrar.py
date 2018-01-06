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

def password(user1):
    with open(PATH_PSSWD, "r") as fichero:
        psswd = None
        for linea in fichero:
            usuario_fichero = linea.split()[1]
            print(usuario_fichero)
            if user1 == usuario_fichero:
                print('coinciden usuarios')
                psswd = linea.split()[3]
                print(psswd)
                break
        return psswd

def checknonce(nonce_usuario, user1):
    function_check = hashlib.md5()
    function_check.update(bytes(str(nonce_usuario), 'utf-8'))
    print('el nonce es: ' + str(nonce_usuario))
    function_check.update(bytes(str((password(user1))), 'utf-8'))
    print('la contraseña es: ' + str(password(user1)))
    return function_check.hexdigest()

class PROXYRegisterHandler(socketserver.DatagramRequestHandler):
    """
    Echo server class
    """
    dic_client = {}
    dic_nonce = {}

    def BaseDatos(self, path):
        self.expired()
        with open(path, "w") as fich:
            for usuario in self.dic_client:
                linea = (usuario + ' ' + self.dic_client[usuario][0] + ' ' +
                         str(self.dic_client[usuario][1]) + ' ' + 
                         self.dic_client[usuario][2] + ' ' +
                         self.dic_client[usuario][3] + '\r\n')
                fich.write(linea)


    def expired(self):
        """
        Darse de baja en el servidor.
        """
        expirados = []
        time_act = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))
        for usuario in self.dic_client:
            if self.dic_client[usuario][3] < time_act:
                expirados.append(usuario)
        for usuario in expirados:
            del self.dic_client[usuario]

    def handle(self):
        """
        handle method of the server class
        (all requests will be handled by this method)
        """
        line = self.rfile.read()
        mensaje = line.decode('utf-8')
        if mensaje:
            print('mensaje: ' + mensaje)
            metodo = mensaje.split()[0]
            if metodo == 'REGISTER':
                t_expires = mensaje.split()[4]
                print('t expires: ' + t_expires)
                usuario = mensaje.split()[1].split(':')[1]
                print('usuario a registrar: ' + usuario)
                direccion = self.client_address[0]
                print('direccion user: ' + direccion)
                puerto = self.client_address[1]
                print('puerto user: ' + str(puerto))
                Authorization = mensaje.split('\r\n')[2].split(':')[0]
                if usuario in self.dic_client:
                    print('usuario en dicc')
                    if t_expires != '0':
                        t_expire = time.strftime('%Y-%m-%d %H:%M:%S', 
                                                 time.gmtime(time.time() + 
                                                 int(t_expires)))
                        self.dic_client[usuario][3] = t_expire
                        self.BaseDatos(PATH_BASEDATOS)
                        self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                    elif t_expires == '0':
                        del self.dic_client[usuario]
                        self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                else:
                    print('usuario no dicc')
                    if Authorization == 'Authorization':
                        print('tercera línea: ' + mensaje.split('\r\n')[2])
                        print('mensaje tiene Autorizacion: ' + algo)
                        ua_response = mensaje.split('\r\n')[2].split()[2].split('"')[1]
                        print('ua response: '+ ua_response)
                        try:
                            pr_response = checknonce(self.dic_nonce[usuario], usuario)
                            print('proxy response: ' + pr_response)
                            if ua_response == pr_response:
                                print('son iguales')
                                t_regist = time.strftime('%Y-%m-%d %H:%M:%S', 
                                                         time.gmtime(time.time()))
                                t_expire = time.strftime('%Y-%m-%d %H:%M:%S', 
                                                    time.gmtime(time.time() + 
                                                    int(t_expires)))
                                self.dic_client[usuario] = [direccion, puerto, 
                                                            t_regist, t_expire]
                                self.BaseDatos(PATH_BASEDATOS)
                                self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                            else:
                                print('no coinciden')
                                self.wfile.write(b"SIP/2.0 400 Bad Request\r\n\r\n")
                        except KeyError:
                            self.wfile.write(b"SIP/2.0 404 User Not Found\r\n\r\n")
                    else:
                        print('no tercera linea')
                        nonce_num = random.randint(0000, 9999)
                        self.dic_nonce[usuario] = nonce_num
                        error = "SIP/2.0 401 Unauthorized\r\n" + 'WWW Authenticate: Digest nonce="' + str(self.dic_nonce[usuario]) + '"' + '\r\n\r\n'
                        self.wfile.write(bytes(error, 'utf-8'))

            elif metodo == 'INVITE':
                if 'INVITE' in mensaje:
                    self.wfile.write(b"SIP/2.0 100 Trying\r\n\r\n")
                    self.wfile.write(b"SIP/2.0 180 Ringing\r\n\r\n")
                    self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                if 'ACK' in mensaje:
                    print('recibo ack')
                
#           elif metodo == 'BYE':
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
