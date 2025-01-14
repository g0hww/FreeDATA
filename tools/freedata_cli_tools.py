#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: DJ2LS

"""

import argparse
import socket
import base64
import json
from pick import pick
import time
import sounddevice as sd

# --------------------------------------------GET PARAMETER INPUTS
parser = argparse.ArgumentParser(description='Simons TEST TNC')
parser.add_argument('--port', dest="socket_port", default=3000, help="Set socket listening port.", type=int)
parser.add_argument('--host', dest="socket_host", default='localhost', help="Set the host, the socket is listening on.", type=str)
args = parser.parse_args()
HOST, PORT = args.socket_host, args.socket_port

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Connect to server
sock.connect((HOST, PORT))


def main_menu():
    while True:
        time.sleep(0.1)
        title = 'Please select a command you want to run: '
        options = ['BEACON', 'PING', 'ARQ', 'LIST AUDIO DEVICES']
        option, index = pick(options, title)

        # BEACON AREA
        if option == 'BEACON':
            option, index = pick(['5',
                                  '10',
                                  '15',
                                  '30',
                                  '45',
                                  '60',
                                  '90',
                                  '120',
                                  '300',
                                  '600',
                                  '900',
                                  '1800',
                                  '3600',
                                  'STOP BEACON',
                                  '----- BACK -----'], "Select beacon interval [seconds]")

            if option == '----- BACK -----':
                main_menu()
            elif option == 'STOP BEACON':
                run_network_command({"type": "broadcast", "command": "stop_beacon"})

            else:
                run_network_command({"type": "broadcast", "command": "start_beacon", "parameter": str(option)})

        elif option == 'PING':
            pass

        elif option == 'ARQ':

            option, index = pick(['GET RX BUFFER', 'DISCONNECT', '----- BACK -----'], "Select ARQ command")

            if option == '----- BACK -----':
                main_menu()
            elif option == 'GET RX BUFFER':
                run_network_command({"type": "get", "command": "rx_buffer"})
            else:
                run_network_command({"type": "arq", "command": "disconnect"})

        elif option == 'LIST AUDIO DEVICES':

            devices = sd.query_devices(device=None, kind=None)
            device_list = []
            for device in devices:
                device_list.append(
                    f"{device['index']} - "
                    f"{sd.query_hostapis(device['hostapi'])['name']} - "
                    f"Channels (In/Out):{device['max_input_channels']}/{device['max_output_channels']} - "
                    f"{device['name']}")

            device_list.append('----- BACK -----')

            option, index = pick(device_list, "Audio devices")

            if option == '----- BACK -----':
                main_menu()

        else:
            print("no menu point found...")


def run_network_command(command):
    command = json.dumps(command)
    command = bytes(command + "\n", 'utf-8')
    sock.sendall(command)


if __name__ == "__main__":
    main_menu()