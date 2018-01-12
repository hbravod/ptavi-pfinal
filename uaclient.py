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


def Log(path, accion, ip, puerto, mensaje):
    f = open(path, "a")
    if accion == 'abrir':
        mensaje = (time.strftime('%Y%m%d%H%M%S', time.gmtime(time.time())) +
                   ' Starting...' + '\r\n')
    elif accion == 'recibir':
        mensaje = (time.strftime('%Y%m%d%H%M%S', time.gmtime(time.time())) +
                   ' Received from ' + ip + ':' + str(puerto) +
                   ': ' + mensaje.replace('\r\n', ' ') + '\r\n')
    elif accion == 'enviar':
        mensaje = (time.strftime('%Y%m%d%H%M%S', time.gmtime(time.time())) +
                   ' Sent to ' + ip + ':' + str(puerto) + ': ' +
                   mensaje.replace('\r\n', ' ') + '\r\n')
    elif accion == 'error':
        mensaje = (time.strftime('%Y%m%d%H%M%S', time.gmtime(time.time())) +
                   ' Error: ' + mensaje.replace('\r\n', ' ') +
                   '\r\n')
    elif accion == 'acabado':
        mensaje = (time.strftime('%Y%m%d%H%M%S', time.gmtime(time.time())) +
                   ' Finishing.' + '\r\n')
    f.write(mensaje)
    f.close()

def checknonce(nonce):
    function_check = hashlib.md5()
    function_check.update(bytes(str(nonce), 'utf-8'))
    print('el nonce es: ' + str(nonce))
    function_check.update(bytes(str(PASSWD), 'utf-8'))
    print('la pass es: ' + str(PASSWD))
    print('cliente: ' + function_check.hexdigest())
    return function_check.hexdigest()


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

if __name__ == "__main__":

    if len(sys.argv) != 4:
        sys.exit("python3 uaclient.py config method option")

    CONFIG = sys.argv[1]
    METHOD = sys.argv[2]
    OPTION = sys.argv[3]

    XMLHandler.elparser()

    if XMLHandler.dicc['regproxy_ip'] is None:
        IP_PROXY = '127.0.0.1'
    else:
        IP_PROXY = XMLHandler.dicc['regproxy_ip']

    PORT_PROXY = int(XMLHandler.dicc['regproxy_puerto'])
    PORT_USER = int(XMLHandler.dicc['uaserver_puerto'])
    print('puerto user: ' + str(PORT_USER))
    USER = XMLHandler.dicc['account_username']
    IP_USER = XMLHandler.dicc['uaserver_ip']
    PORT_CANCION = int(XMLHandler.dicc['rtpaudio_puerto'])
    PASSWD = XMLHandler.dicc['account_passwd']
    CANCION = XMLHandler.dicc['audio_path']
    LOG = XMLHandler.dicc['log_path']

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        my_socket.connect((IP_PROXY, PORT_PROXY))

        if METHOD == "REGISTER":
            mensaje = (METHOD + ' sip:' + USER + ':' + str(PORT_USER) +
                       ' SIP/2.0\r\nExpires: ' + str(OPTION) + '\r\n')
            my_socket.send(bytes(mensaje, 'utf-8') + b'\r\n')
            Log(LOG, 'enviar', IP_PROXY, PORT_PROXY, mensaje)
            try: 
                data = my_socket.recv(1024)
                print('Recibido -- ' + data.decode('utf-8'))
                message_recivied = data.decode('utf-8')
                print('recibo del proxy: ' + message_recivied)
                Log(LOG, 'recibir', IP_PROXY, PORT_PROXY, message_recivied)
                if '401' in message_recivied:
                    print(message_recivied)
                    nonce = message_recivied.split()[5].split('"')[1]
                    print(nonce)
                    respuesta = checknonce(nonce)
                    print('respuesta: ' + respuesta)
                    my_socket.send(bytes(METHOD + ' sip:' + USER + ":" +
                                   str(PORT_USER) + ' SIP/2.0\r\n' +
                                   'Expires: ' + str(OPTION) + '\r\n' +
                                   'Authorization: Digest response="' +
                                   respuesta +
                                   '"' + '\r\n\r\n', 'utf-8'))
                    Log(LOG, 'enviar', IP_PROXY, PORT_PROXY,
                        METHOD + ' sip:' + USER + ":" +
                        str(PORT_USER) + ' SIP/2.0\r\n' +
                        'Expires: ' + str(OPTION) + '\r\n' +
                        'Authorization: Digest response="' +
                        respuesta +
                        '"' + '\r\n\r\n')

                    my_socket.connect((IP_PROXY, PORT_PROXY))
                    data = my_socket.recv(1024)
                    message_recivied = data.decode('utf-8')
                    print(message_recivied)
                    Log(LOG, 'recibir', IP_PROXY, PORT_PROXY, message_recivied)

                elif '400' in message_recivied:
                    print(data.decode('utf-8'))

                elif '404' in message_recivied:
                    print(data.decode('utf-8'))

                elif '405' in message_recivied:
                    print(data.decode('utf-8'))
            except ConnectionRefusedError:
                print('Error: No server listening at ' + IP_PROXY + ' port ' +
                     str(PORT_PROXY))

        elif METHOD == "INVITE":
            mensaje = (METHOD + ' sip:' + OPTION + ' SIP/2.0\r\n' +
                       'Content-Type: ' +
                       'application/sdp\r\n\r\n' + 'v=0\r\n' +
                       'o=' + USER + ' ' + IP_USER + '\r\n' +
                       's=misesion\r\n' + 't=0\r\n' + 'm=audio' +
                       ' ' + str(PORT_CANCION) + ' ' + 'RTP')
            
            my_socket.send(bytes(mensaje, 'utf-8') + b'\r\n')
            Log(LOG, 'enviar', IP_PROXY, PORT_PROXY, mensaje)
            print('mensaje que envia: ' + mensaje)

            try:
                data = my_socket.recv(1024)
                print('Recibido -- ' + data.decode('utf-8'))
                message_recivied = data.decode('utf-8').split()
                print('mensaje recibido:' + '\r\n' + data.decode('utf-8'))

                if '100' in message_recivied:
                    print('recibo 100, 180, 200')
                    user_receptor = message_recivied[12].split('=')[1]
                    print('user_receptor: ' + user_receptor)
                    ip_receptor = message_recivied[13]
                    print('ip_receptor: ' + ip_receptor)
                    port_receptor = message_recivied[17]
                    print('port_receptor: ' + port_receptor)

                    my_socket.send(bytes('ACK sip:' + user_receptor +
                                   ' SIP/2.0\r\n', 'utf-8'))

                    aEjecutar = ('./mp32rtp -i ' + ip_receptor + ' -p ' +
                                 str(port_receptor) + ' < ' + CANCION)
                    print("Vamos a ejecutar", aEjecutar)
                    os.system(aEjecutar)
                    print('Acabao')

                elif '400' in message_recivied:
                    print(data.decode('utf-8'))

                elif '404' in message_recivied:
                    print(data.decode('utf-8'))

                elif '405' in message_recivied:
                    print(data.decode('utf-8'))

            except ConnectionRefusedError:
                exit('Error: No server listening at ' + IP_PROXY + ' port ' +
                     str(PORT_PROXY))

        elif METHOD == "BYE":
            my_socket.send(bytes(METHOD + ' sip:' + OPTION +
                           ' SIP/2.0\r\n', 'utf-8') + b'\r\n')
            Log(LOG, 'enviar', IP_PROXY, PORT_PROXY,
                METHOD + ' sip:' + OPTION + ' SIP/2.0\r\n')

            try:
                data = my_socket.recv(1024)
                print('Recibido -- ' + data.decode('utf-8'))
                message_recivied = data.decode('utf-8').split()
                print('mensaje recibido:' + '\r\n' + data.decode('utf-8'))

                if '400' in message_recivied:
                    print(data.decode('utf-8'))

                elif '404' in message_recivied:
                    print(data.decode('utf-8'))

                elif '405' in message_recivied:
                    print(data.decode('utf-8'))

            except ConnectionRefusedError:
                exit('Error: No server listening at ' + IP_PROXY + ' port ' +
                     str(PORT_PROXY))
print("Fin.")
