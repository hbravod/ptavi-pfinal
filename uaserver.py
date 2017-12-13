#!/usr/binver/python3
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

import os
import socketserver
import sys
from uaclient import XMLHandler


if __name__ == "__main__":
    IP_uaserver = XMLHandler.dicc['uaserver_ip']
    PORT_uaserver = int(XMLHandler.dicc['uaserver_puerto'])
    if len(sys.argv) < 2:
        print("Usage: python3 uaserver.py config")

    XMLHandler.elparser()
    # Creamos servidor de eco y escuchamos
    SERV = socketserver.UDPServer((IP_uaserver, PORT_uaserver))
    print("Listening...")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print('Server Cancelled')
