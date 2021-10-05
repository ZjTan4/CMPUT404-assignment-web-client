#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust, 2021 Zijie Tan
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
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        header = self.get_headers(data)
        header_list = str.split(header, " ") # HTTP/1.1 200 OK\r\n
        try:
            code = int(header_list[1])
        except:
            print("get_code fail")
        return code

    def get_headers(self,data):
        try:
            header, body = str.split(data, '\r\n\r\n')
        except:
            print("get_body fails")
        return header

    def get_body(self, data):
        try:
            header, body = str.split(data, '\r\n\r\n')
        except:
            print("get_body fails")
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock=None):
        if (not sock):
            sock = self.socket
        buffer = bytearray()
        done = False
        while not done:
            #print("post")
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def parse_url(self, url):
        try:
            protocol, uri = str.split(url, "://")
            uri_list = str.split(uri, "/")
            host_port = uri_list[0]

            # compute the path
            path = "/" + "/".join(uri_list[1:])

            # compute the host and port
            host = ""
            port = 80
            if (host_port.find(':') != -1):
                host, port = str.split(host_port, ":")
                port = int(port)
            else:
                host = host_port
        except Exception as e:
            print("get_path fails for {}".format(e))
        return host, port, path

    # example URL: http://127.0.0.1:27600/49872398432
    # format: http://<host>:<port>/<path>
    def GET(self, url, args=None):
        code = 500
        body = ""
        get = "GET {} HTTP/1.1\r\n"
        host, port, path = self.parse_url(url)
        try:
            self.connect(host, port)
            get = get.format(path)
            get += ("Host: {}\r\n\r\n".format(host))
            self.sendall(get)
            buffer = self.recvall()
            code = self.get_code(buffer)
            body = self.get_body(buffer)

            self.close()
        except Exception as e:
            print("Get fail due to {}".format(e))
            sys.exit(1)
        
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        post = "POST {} HTTP/1.1\r\n"
        host, port, path = self.parse_url(url)
        try:
            self.connect(host, port)
            post = post.format(path)
            post += ("Host: {}\r\n".format(host))
            post += "Content-Type: application/x-www-form-urlencoded\r\n"
            if args:
                post_body = ""
                for key, value in enumerate(args):
                    post_body += "{}: {}\r\n".format(key, value)
                body_bytes = post_body.encode("utf-8")
                post += "Content-Length: {}\r\n".format(len(body_bytes))
                post += "\r\n"
                post += post_body
            else:
                post += "Content-Length: 0\r\n"
                post += "\r\n"

            self.sendall(post)
            buffer = self.recvall()
            code = self.get_code(buffer)
            body = self.get_body(buffer)
            self.close()
        except Exception as e:
            print("Post fails due to {}".format(e))
            sys.exit(1)
        
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    #print(len(sys.argv)) # 1 for non-args
    
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3): # (url, command)
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
