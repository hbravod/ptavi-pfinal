#!/usr/binver/python3
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import hashlib
import os
import socket
import socketserver
import sys
import time
import random


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
    dic_nonce = {}

    def Log(path, accion, ip, puerto, mensaje):
        f = open(path, "a")
        if accion == 'abrir':
            mensaje = (time.strftime('%Y%m%d%H%M%S',
                       time.gmtime(time.time())) + ' Starting...' + '\r\n')

        elif accion == 'recibir':
            mensaje = (time.strftime('%Y%m%d%H%M%S',
                       time.gmtime(time.time())) + ' Received from ' + ip +
                       ':' + str(puerto) + ': ' +
                       mensaje.replace('\r\n', ' ') + '\r\n')

        elif accion == 'enviar':
            mensaje = (time.strftime('%Y%m%d%H%M%S',
                       time.gmtime(time.time())) + ' Sent to ' + ip + ':' +
                       str(puerto) + ': '  + mensaje.replace('\r\n', ' ') +
                       '\r\n')

        elif accion == 'error':
            mensaje = (time.strftime('%Y%m%d%H%M%S',
                       time.gmtime(time.time())) + ' Error: ' +
                       mensaje.replace('\r\n', ' ') + '\r\n')

        elif metodo == 'acabado':
            mensaje = (time.strftime('%Y%m%d%H%M%S',
                       time.gmtime(time.time())) + ' Finishing.')

        f.write(mensaje)
        f.close()

    def BaseDatos(self, path):
        """
        Escribe en el fichero database.txt: usuario ip puerto 
        fecha y hora registro fecha y hora de expiración
        """
        self.expired()
        with open(path, "w") as fich:
            for usuario in self.dic_client:
                linea = (usuario + ' ' + self.dic_client[usuario][0] + ' ' +
                         str(self.dic_client[usuario][1]) + ' ' + 
                         str(self.dic_client[usuario][2]) + ' ' +
                         str(self.dic_client[usuario][3]) + '\r\n')
                fich.write(linea)


    def expired(self):
        """
        Darse de baja en el servidor.
        """
        expirados = []
        time_act = time.time()
        print(time_act)
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
        while 1:
            line = self.rfile.read()
            mensaje = line.decode('utf-8')
            if not mensaje:
                break
            print('mensaje: ' + mensaje)
            metodo = mensaje.split()[0]
            if metodo == 'REGISTER':
                #path, accion, ip, puerto, mensaje
                PROXYRegisterHandler.Log(LOG, 'recibir',
                                         IP_SERVER, PORT_SERVER, mensaje)
                t_expires = mensaje.split()[4]
                print('t expires: ' + t_expires)
                usuario = mensaje.split()[1].split(':')[1]
                print('usuario a registrar: ' + usuario)
                direccion = self.client_address[0]
                print('direccion user: ' + direccion)
                puerto = mensaje.split()[1].split(':')[2]
                print('puerto server: ' + str(puerto))
                algo = mensaje.split('\r\n')[2].split(':')[0]
                if usuario in self.dic_client:
                    print('usuario en dicc')
                    if t_expires != '0':
                        t_expire = time.time() + int(t_expires)
                        self.dic_client[usuario][3] = t_expire
                        self.BaseDatos(PATH_BASEDATOS)
                        self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                    elif t_expires == '0':
                        del self.dic_client[usuario]
                        self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                else:
                    print('usuario no dicc')
                    if algo == 'Authorization':
                        print('tercera línea: ' + mensaje.split('\r\n')[2])
                        print('mensaje tiene Autorizacion: ' + algo)
                        ua_response1 = mensaje.split('\r\n')[2]
                        ua_response = ua_response1.split()[2].split('"')[1]
                        print('ua response: '+ ua_response)
                        try:
                            pr_response = checknonce(self.dic_nonce[usuario],
                                                     usuario)
                            print('proxy response: ' + pr_response)
                            if ua_response == pr_response:
                                print('son iguales')
                                t_regist = time.time()
                                t_expire = time.time() + int(t_expires)
                                self.dic_client[usuario] = [direccion, puerto, 
                                                            t_regist, t_expire]
                                self.BaseDatos(PATH_BASEDATOS)
                                self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                            else:
                                print('no coinciden')
                                error400 = "SIP/2.0 400 Bad Request\r\n\r\n"
                                self.wfile.write(berror400)
                        except KeyError:
                            error404 = "SIP/2.0 404 User Not Found\r\n\r\n"
                            self.wfile.write(berror404)
                    else:
                        print('no tercera linea')
                        nonce_num = random.randint(0000, 9999)
                        self.dic_nonce[usuario] = nonce_num
                        error = ("SIP/2.0 401 Unauthorized\r\n" +
                                 'WWW-Authenticate: Digest nonce="' +
                                 str(self.dic_nonce[usuario]) + '"' +
                                 '\r\n\r\n')
                        self.wfile.write(bytes(error, 'utf-8'))

            elif metodo == 'INVITE':
                emite = mensaje.split('\r\n')[4].split()[0][2:] # client1
                print('emite: ' + emite)
                recibe = mensaje.split()[1].split(':')[1] # client2
                print('recibe: ' + str(recibe))
                if emite in self.dic_client and recibe in self.dic_client:
                    print('usuarios en dic')
                    recibe_ip = self.dic_client[recibe][0] # client2
                    print('ip_recibe: ' + str(recibe_ip))
                    emite_ip = self.dic_client[emite][0] # client1
                    print('ip_envia: ' + str(emite_ip))
                    recibe_port = self.dic_client[recibe][1] # client2
                    print('port_recibe: ' + str(recibe_port))
                    emite_port = self.dic_client[emite][1] # client1
                    print('port_envia: ' + str(emite_port))
                    try:
                        with socket.socket(socket.AF_INET,
                                           socket.SOCK_DGRAM) as my_socket:
                            my_socket.setsockopt(socket.SOL_SOCKET,
                                                 socket.SO_REUSEADDR, 1)
                            my_socket.connect((recibe_ip, int(recibe_port))) # client2
                            my_socket.send(bytes(mensaje, 'utf-8'))
                            data = my_socket.recv(1024)
                            print('respuesta receptor a invite: ' +
                                  data.decode('utf-8'))
                        self.wfile.write(bytes(data.decode('utf-8'), 'utf-8'))
                    except ConnectionRefusedError:
                        print('Error: No server listening at ' + recibe_ip + ' port ' +
                             str(recibe_port))
                        self.wfile.write(b"SIP/2.0 404 User Not Found\r\n\r\n")
                else:
                    print('no users dic')
                    self.wfile.write(b"SIP/2.0 404 User Not Found\r\n\r\n")

            elif metodo == 'ACK':
                metodo = mensaje.split()[0]
                print('metodo: ' + metodo)
                emite = mensaje.split()[1].split(':')[1]
                print('emite: ' + emite)
                if emite in self.dic_client:
                    ip_emite = self.dic_client[emite][0]
                    print('emite_ip: ' + ip_emite)
                    port_emite = self.dic_client[emite][1]
                    print('emite_port: ' + str(port_emite))
                    try:
                        with socket.socket(socket.AF_INET,
                                           socket.SOCK_DGRAM) as my_socket:
                            my_socket.setsockopt(socket.SOL_SOCKET,
                                                 socket.SO_REUSEADDR, 1)
                            my_socket.connect((ip_emite, int(port_emite)))
                            my_socket.send(bytes(mensaje, 'utf-8'))
                    except ConnectionRefusedError:
                        print('Error: No server listening at ' + ip_emite + ' port ' +
                             str(port_emite))
                        self.wfile.write(b"SIP/2.0 404 User Not Found\r\n\r\n")
                else:
                    print('no users dic')
                    self.wfile.write(b"SIP/2.0 404 User Not Found\r\n\r\n")

            elif metodo == 'BYE':
                recibe = mensaje.split()[1].split(':')[1] # client2
                print('recibe: ' + str(recibe))
                if recibe in self.dic_client:
                    print('receptor en dicc')
                    ip_recibe = self.dic_client[recibe][0] # 127.0.0.1
                    port_recibe = self.dic_client[recibe][1] # 6005
                    print('ip recibe: ' + ip_recibe)
                    print('port recibe: ' + str(port_recibe))
                    try:
                        with socket.socket(socket.AF_INET,
                                           socket.SOCK_DGRAM) as my_socket:
                            my_socket.setsockopt(socket.SOL_SOCKET,
                                                 socket.SO_REUSEADDR, 1)
                            my_socket.connect((ip_recibe, int(port_recibe)))
                            my_socket.send(bytes(mensaje, 'utf-8'))
                            data = my_socket.recv(1024)
                            print('respuesta de recibe en INVITE: ' +
                                  data.decode('utf-8'))
                        self.wfile.write(bytes(data.decode('utf-8'), 'utf-8'))
                    except ConnectionRefusedError:
                        print('Error: No server listening at ' + ip_recibe + ' port ' +
                             str(port_recibe))
                        self.wfile.write(b"SIP/2.0 404 User Not Found\r\n\r\n")
                else:
                    print('no users dic')
                    self.wfile.write(b"SIP/2.0 404 User Not Found\r\n\r\n")

            else:
                self.wfile.write(b"SIP/2.0 405 Method Not Allowed\r\n\r\n")

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
    PATH_PSSWD = PROXYHandler.dicc['database_passwdpath']
    LOG = PROXYHandler.dicc['log_path']

    # path, accion, ip, puerto, mensaje
    PROXYRegisterHandler.Log(LOG, 'abrir', None, None, None)

    serv = socketserver.UDPServer((IP_SERVER, PORT_SERVER),
                                   PROXYRegisterHandler)
    print("Server " + NAME_SERVER + " listening at port " +
          str(PORT_SERVER) + "...")

    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print('Server Closed')
