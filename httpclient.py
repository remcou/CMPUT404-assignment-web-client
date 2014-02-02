#!/usr/bin/env python
# coding: utf-8
# Copyright 2014 Remco Uittenbogerd
# Copyright 2013 Abram Hindle
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import urllib
import urlparse

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPRequest(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def connect(self, host, port):
        sock = socket.create_connection( (host,port), 5 )
        return sock

    def get_code(self, data):
        return int( data.split(" ")[1] )

    def get_headers(self,data):
        return data.split("\r\n\r\n")[0]

    def get_body(self, data):
        split = data.split("\r\n\r\n")
        if len(split) >= 2:
            return split[1]
        else:
            return None

    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)
        
    def connect_and_parse_url( self, url ):
        url = url if url.startswith( "http" ) else "http://" + url
        parsedurl = urlparse.urlparse(url)
		
        port = parsedurl.port if parsedurl.port else 80
        host = parsedurl.hostname
        path = parsedurl.path if parsedurl.path else "/"
		
        sock = self.connect( host, port )
        
        return sock, host, path

    def GET(self, url, args=None):
        sock, host, path = self.connect_and_parse_url( url )   
        
        data = "GET %s HTTP/1.1\r\n" % path
        data += "host: %s\r\n" % host
        data += "connection: close\r\n\r\n"
        
        sock.sendall( data )
        data = self.recvall( sock )
        
        return HTTPRequest( self.get_code( data ), self.get_body( data ) )

    def POST(self, url, args=None):
        sock, host, path = self.connect_and_parse_url( url )
        
        header = "POST %s HTTP/1.1\r\n" % path
        header += "host: %s\r\n" % host
        header += "content-type: application/x-www-form-urlencoded\r\n"
        header += "connection: close\r\n"
        
        body = ""
        if args:
            args = urllib.urlencode(args)
            header += "content-length: %i\r\n" % len(args)
            body += args
        
        data = "%s\r\n%s" % ( header, body )
        sock.sendall( data )
        data = self.recvall( sock )
        
        return HTTPRequest( self.get_code( data ), self.get_body( data ) )

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[2], sys.argv[1] )
    else:
        print client.command( command, sys.argv[1] )    
