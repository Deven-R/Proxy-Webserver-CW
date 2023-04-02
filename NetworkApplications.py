#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import argparse
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
        
        parser_p = subparsers.add_parser('ping', aliases=['p'], help='run ping')
        parser_p.set_defaults(timeout=4)
        parser_p.add_argument('hostname', type=str, help='host to ping towards')
        parser_p.add_argument('--count', '-c', nargs='?', type=int,
                              help='number of times to ping the host before stopping')
        parser_p.add_argument('--timeout', '-t', nargs='?',
                              type=int,
                              help='maximum timeout before considering request lost')
        parser_p.set_defaults(func=ICMPPing)

        parser_t = subparsers.add_parser('traceroute', aliases=['t'],
                                         help='run traceroute')
        parser_t.set_defaults(timeout=4, protocol='icmp')
        parser_t.add_argument('hostname', type=str, help='host to traceroute towards')
        parser_t.add_argument('--timeout', '-t', nargs='?', type=int,
                              help='maximum timeout before considering request lost')
        parser_t.add_argument('--protocol', '-p', nargs='?', type=str,
                              help='protocol to send request with (UDP/ICMP)')
        parser_t.set_defaults(func=Traceroute)
        
        parser_pt = subparsers.add_parser('paris-traceroute', aliases=['pt'],
                                         help='run paris-traceroute')
        parser_pt.set_defaults(timeout=4, protocol='icmp')
        parser_pt.add_argument('hostname', type=str, help='host to traceroute towards')
        parser_pt.add_argument('--timeout', '-t', nargs='?', type=int,
                              help='maximum timeout before considering request lost')
        parser_pt.add_argument('--protocol', '-p', nargs='?', type=str,
                              help='protocol to send request with (UDP/ICMP)')
        parser_pt.set_defaults(func=ParisTraceroute)

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

class ICMPPing(NetworkApplication):

    def receiveOnePing(self, icmpSocket, destinationAddress, ID, timeout):
        # 1. Wait for the socket to receive a reply
        # 2. Once received, record time of receipt, otherwise, handle a timeout
        # 3. Compare the time of receipt to time of sending, producing the total network delay
        # 4. Unpack the packet header for useful information, including the ID
        # 5. Check that the ID matches between the request and reply
        # 6. Return total network delay
        pass

    def sendOnePing(self, icmpSocket, destinationAddress, ID):
        # 1. Build ICMP header
        # 2. Checksum ICMP packet using given function
        # 3. Insert checksum into packet
        AF_INET, SOCK_RAW, IPPROTO_ICMP
        # 4. Send packet using socket
        # 5. Record time of sending
        os.getpid() & 0xFFFF

        delay = self.receiveOnePing(icmpSocket, destinationAddress, ID, timeout)
        pass

    def doOnePing(self, destinationAddress, timeout):
        # 1. Create ICMP socket
        # 2. Call sendOnePing function
        # 3. Call receiveOnePing function
        # 4. Close ICMP socket
        # 5. Return total network delay
        pass

    def __init__(self, args):
        print('Ping to: %s...' % (args.hostname))
        # 1. Look up hostname, resolving it to an IP address
        # 2. Call doOnePing function, approximately every second
        # 3. Print out the returned delay (and other relevant details) using the printOneResult method
        self.printOneResult('1.1.1.1', 50, 20.0, 150) # Example use of printOneResult - complete as appropriate
        # 4. Continue this process until stopped


class Traceroute(NetworkApplication):

    def __init__(self, args):
        # Please ensure you print each result using the printOneResult method!
        print('Traceroute to: %s...' % (args.hostname))

class ParisTraceroute(NetworkApplication):

    def __init__(self, args):
        # Please ensure you print each result using the printOneResult method!
        print('Paris-Traceroute to: %s...' % (args.hostname))

class WebServer(NetworkApplication):

    def handleRequest(tcpSocket):
        # 1. Receive request message from the client on connection socket
        # 2. Extract the path of the requested object from the message (second part of the HTTP header)
        # 3. Read the corresponding file from disk
        # 4. Store in temporary buffer
        # 5. Send the correct HTTP response error
        # 6. Send the content of the file to the socket
        # 7. Close the connection socket
        pass

    def __init__(self, args):
        print('Web Server starting on port: %i...' % (args.port))
        # 1. Create server socket
        # 2. Bind the server socket to server address and server port
        # 3. Continuously listen for connections to server socket
        # 4. When a connection is accepted, call handleRequest function, passing new connection socket (see https://docs.python.org/3/library/socket.html#socket.socket.accept)
        # 5. Close server socket


class Proxy(NetworkApplication):

    def __init__(self, args):
        print('Web Proxy starting on port: %i...' % (args.port))
        print('Web Proxy starting on port: %i...' % (args.host))
        proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        proxy_socket.bind(('127.0.0.1', args.port))
        proxy_socket.listen(100)

        client_socket, client_address = proxy_socket.accept()
        print(f'Accepted connection from {client_address[0]}:{client_address[1]}')
        self.handle_request(client_socket)

    def handleRequest(client_socket):
        # 1. Receive request message from the client on connection socket
        received_message = client_socket.recv(9000)
        
        # 2. Extract the path of the requested object from the message (second part of the HTTP header)
        target_port = 80
        target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        target_socket.connect(('127.0.0.1', target_port))
        target_socket.sendall(received_message)
        
        # 3. Read the corresponding file from disk
        
        response_message = target_socket.recv(9000)
        client_socket.send(response_message)
        

        target_socket.close()
        client_socket.close()
        
        pass  






if __name__ == "__main__":
    args = setupArgumentParser()
    args.func(args)

class Proxy(NetworkApplication):

    def __init__(self, args):
        print('Web Server starting on port: %i...' % (args.port))
        self.run_proxy()

    def run_proxy(self):
        proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        proxy_address = ('127.0.0.1', 8080)
        proxy_socket.bind(proxy_address)
        proxy_socket.listen(1)

        client_socket, client_address = proxy_socket.accept()
        request = self.receive_request(client_socket)
        response = self.forward_request(request)
        self.send_response(client_socket, response)

        proxy_socket.close()
        client_socket.close()

    def receive_request(self, client_socket):
        request = client_socket.recv(9000)
        return request

    def forward_request(self, request):
        target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        target_address = ('www.neverssl.com', 80)
        target_socket.connect(target_address)
        target_socket.send(request)
        response = target_socket.recv(9000)
        target_socket.close()
        return response

    def send_response(self, client_socket, response):
        client_socket.send(response)

def cache_or_forward_request(self, request):
        # Object caching functionality - Store a copy of the response data in a local file
        if not os.path.exists('cache'):
            os.mkdir('cache')
        
        filename = request.split('/')[-1]
        filepath = 'cache/' + filename
        
        if os.path.exists(filepath):
            # load the response from the local file
            with open(filepath, 'rb') as f:
                response = f.read()
        else:
            # forward the request to the target server and receive the response
            target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_address = ('www.neverssl.com', 80)
            target_socket.connect(target_address)
            target_socket.send(request)
            response = target_socket.recv(9000)
            target_socket.close()
        
            # save the response to a local file
            with open(filepath, 'wb') as f:
                f.write(response)
        
        return response 


        # This is a Python class definition for a proxy server that extends a NetworkApplication class

class Proxy(NetworkApplication):

    # The __init__() method is called when an object is created from this class.
    # It takes a single argument 'args' and prints a message indicating that the Web Server is starting on a particular port number.
    def __init__(self, args):
        print('Web Server starting on port: %i...' % (args.port))
        # calls the run_proxy() method to start the server.
        self.run_proxy()

    # The run_proxy() method is responsible for starting the proxy server, binding the socket to the port number specified, and accepting incoming connections.
    def run_proxy(self):
        # Create a socket object using AF_INET address family and SOCK_STREAM socket type.
        proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Set up the address for the socket to listen on, which is localhost and the port number specified in the args object.
        proxy_address = ('localhost', args.port)
        # Bind the socket to the address specified
        proxy_socket.bind(proxy_address)
        # Listen for incoming connections, with a maximum of 1 connection waiting to be accepted
        proxy_socket.listen(1)

        # The server runs forever and listens for incoming connections.
        while True:
            # accept a connection when one is requested, the accept() method returns a tuple containing the socket object for the client and the client's address.
            client_socket, client_address = proxy_socket.accept()
            # receive the request data from the client
            request = self.receive_request(client_socket)
            # print the request data to the console
            print(request)
            # check if the request data is already cached, if it is then retrieve it from the cache and return it to the client
            # if it is not, forward the request to the target server, receive the response and cache it for future requests
            response = self.cache_or_forward_request(request)
            # send the response data to the client
            self.send_response(client_socket, response)
            # close the client socket connection
            self.close_sockets(client_socket)
        

    # The receive_request() method is responsible for receiving data from the client socket and returning it.
    def receive_request(self, client_socket):
        # receive the request data from the client socket with a maximum buffer size of 9000 bytes.
        request = client_socket.recv(9000)
        return request

    # The cache_or_forward_request() method is responsible for checking if the requested object is already in cache or not.
    # If it is not, it forwards the request to the target server, receives the response and caches it.
    def cache_or_forward_request(self, request):
        # Check if the 'cache' directory exists, and create it if it doesn't.
        if not os.path.exists('cache'):
            os.mkdir('cache')
        
        # Extract the filename from the request and construct a filepath
        filename = request.decode().split(' ')[1].replace("http://", "").replace("/", "")
        filepath = 'cache/' + filename
        
        if os.path.exists(filepath):
            # If the response has been cached, read it from the local file
            print("This file exists")
            with open(filepath, 'rb') as f:
                response = f.read()
        else:
            # If the response hasn't been cached, forward the request to the target server and receive the response
            target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_address = (filename, 80)
            target_socket.connect(target_address)
            target_socket.send(request)
            response = target_socket.recv(9000)
            target_socket.close()
        
            # Save the response to a local file
            with open(filepath, 'wb') as f:
                f.write(response)
        
        # Return the response
        return response 

    def send_response(self, client_socket, response):
        # Send the response to the client
        client_socket.send(response)

    def close_sockets(self, client_socket):
        # Close the client socket
        client_socket.close()

          # forward the request to the target server and receive the response
            request_method = request.decode().split(' ')[0]
            if request_method == 'GET':