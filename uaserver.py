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


class EchoHandler(socketserver.DatagramRequestHandler):
    """
    Echo server class
    """
    dicc_rtp = {} #dicc con clave ip y valor puerto

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

    def BuscaPuerto(self, ip):
        for usuario in self.dicc_rtp:
            if ip == usuario:
                puerto = self.dicc_rtp[usuario]
                break
        return puerto

    def Log(path, accion, ip, puerto, mensaje):
        f = open(path, "a")
        if accion == 'abrir':
            mensaje = (time.strftime('%Y%m%d%H%M%S',time.gmtime(time.time())) + ' Starting...' + '\r\n')
        elif accion == 'recibir':
            mensaje = (time.strftime('%Y%m%d%H%M%S',time.gmtime(time.time()))+ ' Received from ' + ip + ':' + str(port) + ': ' + mensaje.replace('\r\n', ' ') + '\r\n')
        elif accion == 'enviar':
            mensaje = (time.strftime('%Y%m%d%H%M%S',time.gmtime(time.time())) + ' Sent to '
    + ip + ':' + str(port) + ': '  + mensaje.replace('\r\n', ' ') + '\r\n')
        
        elif Accion == 'error':
            mensaje = (time.strftime('%Y%m%d%H%M%S',time.gmtime(time.time())) + ' Error: ' + mensaje.replace('\r\n', ' ') + '\r\n')
        elif metodo == 'acabado':
            mensaje = (time.strftime('%Y%m%d%H%M%S',time.gmtime(time.time())) + ' Finishing.')
        f.write(mensaje) 
        f.close()

    def handle(self):
        # Escribe dirección y puerto del cliente (de tupla client_address)
        lista = ['INVITE', 'ACK', 'BYE']
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            recivo = self.rfile.read()
            mensaje = recivo.decode('utf-8')
            print('recibo cliente:' +'\r\n')
            print(mensaje)
            method = mensaje.split(' ')[0]
            print('metodo: ' + str(method))
            #Log(LOG, mensaje, 'recibir')
            if not mensaje:
                break

            if method not in lista:
                self.wfile.write(b"SIP/2.0 405 Method Not Allowed \r\n\r\n")

            if method == 'INVITE':
                ip_emite = mensaje.split()[7]
                print('emite_ip: "' + ip_emite + '"')
                port_emite = mensaje.split()[11]
                print('emite_port: ' + port_emite)
                self.dicc_rtp[ip_emite] = port_emite
                self.wfile.write(bytes("SIP/2.0 100 Trying \r\n\r\n" +
                                       "SIP/2.0 180 Ringing \r\n\r\n" +
                                       "SIP/2.0 200 OK \r\n" + 
                                       'Content-Type: '+ 'application/sdp\r\n\r\n'
                                       + 'v=0\r\n' + 'o=' + USER + ' ' +
                                       str(IP_USER) + '\r\n' + 's=misesion\r\n' +
                                       't=0\r\n'+'m=audio' + ' ' + str(PORT_CANCION)
                                       + ' ' + 'RTP\r\n', 'utf-8'))

            elif method == lista[1]:
                ip_emite = self.client_address[0]
                print('emite_ip: ' + ip_emite)    
                port_emite = self.BuscaPuerto(ip_emite)
                print('emite_port: ' + str(port_emite))
                aEjecutar = './mp32rtp -i ' + ip_emite + ' -p ' + str(port_emite) + ' < ' + CANCION
                print("Vamos a ejecutar", aEjecutar)
                os.system(aEjecutar)
                print('acabao')

            elif method == lista[2]:
                self.wfile.write(b"SIP/2.0 200 OK \r\n\r\n")

            elif self.error(mensaje):
                self.wfile.write(b"SIP/2.0 400 Bad Request \r\n\r\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 uaserver.py config")

    CONFIG = sys.argv[1]
    XMLHandler.elparser()
    IP_PROXY = XMLHandler.dicc['regproxy_ip']
    PORT_PROXY = int(XMLHandler.dicc['regproxy_puerto'])
    USER = XMLHandler.dicc['account_username']
    IP_USER = XMLHandler.dicc['uaserver_ip']
    PORT_USER = int(XMLHandler.dicc['uaserver_puerto'])
    PORT_CANCION = int(XMLHandler.dicc['rtpaudio_puerto'])
    CANCION = XMLHandler.dicc['audio_path']

    # Creamos servidor de eco y escuchamos
    try:
        SERV = socketserver.UDPServer((IP_USER, PORT_USER), EchoHandler)
        print("Listening...")
        try:
            SERV.serve_forever()
        except KeyboardInterrupt:
            print('Server Cancelled')
    except ConnectionRefusedError:
        exit("Error: no server listening at " + IP_PROXY + " port " + str(PORT_PROXY))
