#!/usr/bin/python

from codecs import ignore_errors
import sys
import socket
import re

def getContentCharset(head):
    try:
        result = re.search(b'charset=(.*?)\\r', head)
        #return result.group(1).decode("utf-8")
        return 'unicode_escape'
    except:
        return 'unicode_escape'

def getContentLength(head):
    try:
        result = re.search(b'Content-Length:(.*?)\\r', head)
        return int(result.group(1).decode("utf-8"))
    except:
        return 1024

def recv_all(sock):
    sock.settimeout(3)

    fragments = []
    chunk = sock.recv(1024)
    fragments.append(chunk)

    contentCharset = getContentCharset(chunk)
    contentLength = getContentLength(chunk)

    if (contentLength == 1024):
        while 1:
            try:
                chunk = sock.recv(1024)
                if chunk:
                    fragments.append(chunk)
            except socket.timeout:
                print('All chunks received')
                break  
    else:
        counter = 1024
        while counter < contentLength:
            try:
                chunk = sock.recv(1024)
                fragments.append(chunk)
                counter += len(chunk)
            except socket.timeout:
                print('All chunks received')
                break  

    return b''.join(fragments).decode(contentCharset)

def getRequest(host, port, uri):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        request =  'GET' + " / HTTP/1.1\r\nHost:%s\r\n\r\n" % host
        s.sendall(request.encode())
        data = recv_all(s)
        datasplit = str(data).rpartition('<!')
        with open('head.html','w') as f:
            f.write(data)
        with open('site.html','w') as f:
            f.write('<!'+datasplit[2])
        s.close

def headRequest(host, port, uri):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        request =  'HEAD' + " / HTTP/1.1\r\nHost:%s\r\n\r\n" % host
        s.sendall(request.encode())
        data = recv_all(s)
        with open('head.html','w') as f:
            f.write(str(data))
        s.close

def putRequest(host, port, uri):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        connectResponse = s.recv(1024)
        print(connectResponse.decode())
        string = input("Give the string you want to place in a new file: ")
        request = 'PUT ' + uri + ' ' + string
        s.send(request.encode())
        data = s.recv(1024)
        print(data)

def postRequest(host, port, uri):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        connectResponse = s.recv(1024)
        print(connectResponse.decode())
        string = input("Give the string you want to append: ")
        request = 'POST ' + uri + ' ' + string
        s.send(request.encode())
        data = s.recv(1024)
        print(data)

def main(argv):
    try:
        COMMAND = argv[0] # The command used for the HTTP request
        HOST = argv[1]  # The server's hostname or IP address
        PORT = int(argv[2])  # The port used by the server
        URI = argv[3]  # The server's hostname or IP address
        print('HTTP Command: ', argv[0])
        print('SERVER: ', argv[1])
        print('PORT: ', argv[2])
        print('URI: ', argv[3])

    except:
        print('Four arguments needed')
        sys.exit(2)
    
    if COMMAND == 'GET':
        getRequest(HOST, PORT, URI)
    elif COMMAND == 'HEAD':
        headRequest(HOST, PORT, URI)
    elif COMMAND == 'PUT':
        putRequest(HOST, PORT, URI)
    elif COMMAND == 'POST':
        postRequest(HOST, PORT, URI)
    else:
        print('Invalid commands given.')
        print('arg1: HTTP Command')
        print('arg2: HOST')
        print('arg3: Port')
        print('arg4: URI')
        sys.exit(2)

if __name__ == "__main__":
   main(sys.argv[1:])