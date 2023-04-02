#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import argparse
import select
import socket
import os
import sys
import struct
import time
import random
import traceback # useful for exception handling
import threading

def setupArgumentParser() -> argparse.Namespace:
        parser = argparse.ArgumentParser(
            description='A collection of Network Applications developed for SCC.203.')
        parser.set_defaults(func=ICMPPing, hostname='lancaster.ac.uk')
        subparsers = parser.add_subparsers(help='sub-command help')

        parser_w = subparsers.add_parser('web', aliases=['w'], help='run web server')
        parser_w.set_defaults(port=8080)
        parser_w.add_argument('--port', '-p', type=int, nargs='?',
                              help='port number to start web server listening on')
        parser_w.set_defaults(func=WebServer)

        parser_x = subparsers.add_parser('proxy', aliases=['x'], help='run proxy')
        parser_x.set_defaults(port=8000)
        parser_x.add_argument('--port', '-p', type=int, nargs='?',
                              help='port number to start web server listening on')
        parser_x.set_defaults(func=Proxy)

        args = parser.parse_args()
        return args


class NetworkApplication:

    def checksum(self, dataToChecksum: str) -> str:
        csum = 0
        countTo = (len(dataToChecksum) // 2) * 2
        count = 0

        while count < countTo:
            thisVal = dataToChecksum[count+1] * 256 + dataToChecksum[count]
            csum = csum + thisVal
            csum = csum & 0xffffffff
            count = count + 2

        if countTo < len(dataToChecksum):
            csum = csum + dataToChecksum[len(dataToChecksum) - 1]
            csum = csum & 0xffffffff

        csum = (csum >> 16) + (csum & 0xffff)
        csum = csum + (csum >> 16)
        answer = ~csum
        answer = answer & 0xffff
        answer = answer >> 8 | (answer << 8 & 0xff00)

        answer = socket.htons(answer)

        return answer

    def printOneResult(self, destinationAddress: str, packetLength: int, time: float, ttl: int, destinationHostname=''):
        if destinationHostname:
            print("%d bytes from %s (%s): ttl=%d time=%.2f ms" % (packetLength, destinationHostname, destinationAddress, ttl, time))
        else:
            print("%d bytes from %s: ttl=%d time=%.2f ms" % (packetLength, destinationAddress, ttl, time))

    def printAdditionalDetails(self, packetLoss=0.0, minimumDelay=0.0, averageDelay=0.0, maximumDelay=0.0):
        print("%.2f%% packet loss" % (packetLoss))
        if minimumDelay > 0 and averageDelay > 0 and maximumDelay > 0:
            print("rtt min/avg/max = %.2f/%.2f/%.2f ms" % (minimumDelay, averageDelay, maximumDelay))

    def printMultipleResults(self, ttl: int, destinationAddress: str, measurements: list, destinationHostname=''):
        latencies = ''
        noResponse = True
        for rtt in measurements:
            if rtt is not None:
                latencies += str(round(rtt, 3))
                latencies += ' ms  '
                noResponse = False
            else:
                latencies += '* ' 

        if noResponse is False:
            print("%d %s (%s) %s" % (ttl, destinationHostname, destinationAddress, latencies))
        else:
            print("%d %s" % (ttl, latencies))


class WebServer(NetworkApplication):

    def __init__(self, args):

        print('Web Server starting on port: %i...' % (args.port))
        
        # 1. Create server socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # 2. Bind the server socket to server address and server port
        
        self.server_socket.bind(('127.0.0.1', args.port))
        
        # 3. Continuously listen for connections to server socket
        self.server_socket.listen()
        
        while True:
            # 4. When a connection is accepted, call handleRequest function, passing new connection socket
            connection_socket, client_address = self.server_socket.accept()
            self.handleRequest(connection_socket)
        
        # 5. Close server socket
        self.server_socket.close()
        
    def handleRequest(self, tcpSocket):
        # 1. Receive request message from the client on connection socket
        message = tcpSocket.recv(1024).decode()
        print(message)
        
        # 2. Extract the path of the requested object from the message (second part of the HTTP header)
        request_path = message.split()[1]
        file_path = os.path.join(os.getcwd(), request_path[1:])
        print(file_path)
        
        # 3. Read the corresponding file from disk
        try:
            with open(file_path, 'rb') as file:
                content = file.read()
        except FileNotFoundError:
            # 5. Send the correct HTTP response error
            response = "HTTP/1.1 404 Not Found\r\n\r\n"
            tcpSocket.sendall(response.encode())
            tcpSocket.close()
            return
        
        # 6. Send the content of the file to the socket
        response = "HTTP/1.1 200 OK\r\n\r\n"
        tcpSocket.sendall(response.encode() + content)
        
        # 7. Close the connection socket
        tcpSocket.close()


class Proxy(NetworkApplication):

    # It takes argument 'args' prints that the Web Server is starting
    # Configurable port number !!
    #def __init__(self, args):
      #  print('Web Server starting on port: %i...' % (args.port))
        # calls the run_proxy() method to start the server.
        #self.run_proxy()

    # This method is responsible for starting the proxy server, binding the socket and listening for connections. 
    def run_proxy(self):

        # Create a proxy socket
        proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Set up the address for the socket to listen on, which is localhost and the port number specified in the args object.
        
        # Bind the socket to the address specified
        
        proxy_socket.bind(('localhost', 8000))
        
        # Listen for incoming connections, with a maximum of 1 
        proxy_socket.listen(1)

        # The server runs infinitly and listens for connections.
        while True:
            
            # accept a connection when one is requested, the accept() method returns a tuple containing the socket object for the client and the client's address.
            client_socket, client_address = proxy_socket.accept()
            
            request = self.receive_request(client_socket)
            
            # print the request data to the console
            print(request)
            
            response = self.cache_or_forward_request(request)
            
            # send the response data to the client
            self.send_response(client_socket, response)
            
            # close the client socket connection
            self.close_sockets(client_socket)
        

    # The receive_request() method is responsible for receiving data from the client socket and returning it.
    def receive_request(self, client_socket):
        # receive the request data from the client socket with a size of 9000 bytes.
        request = client_socket.recv(9000)
        return request

    # The cache_or_forward_request() method is responsible for checking if the requested object is already in cache or not.

    def cache_or_forward_request(self, request):
       
        # Check if the cache directory exists, and create it if it doesn't.
        if not os.path.exists('cache'):
            os.mkdir('cache')
        
        # Decode and split (EXTRACTION) the filename from the request and construct a filepath
        filename = request.decode().split(' ')[1].replace("http://", "").replace("/", "")
        filepath = 'cache/' + filename
        
        if os.path.exists(filepath):
            # If the response has been cached, read it from the local file
            print("This file exists")
            with open(filepath, 'rb') as f:
                response = f.read()
            f.close()
        else:
            # If the response hasn't been cached, forward the request to the target server and receive the response
            # forward the request to the target server and receive the response
            request_type = request.decode().split(' ')[0]
            print("tHIS IS THE REQUEST TYPE: ", request_type)
            
            if request_type == 'GET':
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_address = (filename, 80)
                server_socket.connect(server_address)
                server_socket.send(request)
                response = server_socket.recv(9000)
                server_socket.close()
            
            else:

                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_address = (filename, 80)
                server_socket.connect(server_address)
                server_socket.send(request)
                response = server_socket.recv(9000)
                server_socket.close()

            
            # Save the response to CACHE 
            with open(filepath, 'wb') as f:
                f.write(response)
            f.close()
        
        
        return response 

    def send_response(self, client_socket, response):
        
        client_socket.send(response)

    def close_sockets(self, client_socket):
        # Close the client socket
        client_socket.close()


    # It takes argument 'args' prints that the Web Server is starting
    # Configurable port number !!
    def __init__(self, args):
        print('Web Server starting on port: %i...' % (args.port))
        # calls the run_proxy() method to start the server.
        self.run_proxy()


if __name__ == "__main__":
    args = setupArgumentParser()
    args.func(args)

