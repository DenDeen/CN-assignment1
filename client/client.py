#!/usr/bin/python

from codecs import ignore_errors
from posixpath import split
from bs4 import BeautifulSoup
import sys
import select
import socket
import re
import os


def getContentCharset(head):
    try:
        result = re.search(b'charset=(.*?)\\r', head)
        return result.group(1).decode("utf-8")
    except:
        return 'unicode_escape'

def getContentLength(head):
    try:
        result = re.search(b'Content-Length:(.*?)\\r', head)
        return int(result.group(1).decode("utf-8"))
    except:
        return 2048

def recv_all(sock):
    chunks = b''
    chunk = sock.recv(2048)
    chunks += chunk

    contentCharset = getContentCharset(chunk)
    contentLength = getContentLength(chunk)

    if (contentLength <= 2048):
        while select.select([sock], [], [], 3)[0]:
            data = sock.recv(2048)
            if not data: 
                break
            chunks += data
    else:
        counter = 2048
        while counter < contentLength:
            chunk = sock.recv(2048)
            chunks += chunk
            counter += len(chunk)

    headers_data = chunks.split(b'\r\n\r\n')[0]
    html_data = chunks[len(headers_data)+4:]
    return headers_data, html_data 

def getHost(host):
    result = re.search('(?<=\.).*(?=\.)', host.split('/')[0]).group(0)
    if (result == '0.0'):
        return 'localhost'
    else:
        return result
    
def splitHost(host):
    return host.split("/",1)    

def getUrl(host):
    if len(splitHost(host)) > 1:
        return splitHost(host)[1]
    else:
        return "/"
    
def createPaths(file):
    path = os.path.join(os.getcwd(),os.path.join("client", getHost(file)))
    if not os.path.isdir(path):
        print("making dir: " + path)
        os.makedirs (path, mode=0o777, exist_ok=False)
    return path

def getRequest(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        hostSplit = splitHost(host)[0]
        s.connect((hostSplit, port))

        request =  'GET ' + getUrl(host) +" HTTP/1.1\r\nHost: %s\r\n\r\n" % hostSplit
        s.sendall(request.encode())
        _, html_data = recv_all(s)
        path = createPaths(host) 

        with open(path + '\\index.html','wb') as f:
            f.write(html_data)

        soup = ''
        with open(path + '\\index.html') as f:
            soup = BeautifulSoup(f, "html.parser")
            i = 1
            for img in soup.find_all("img"):
                try:
                    img_uri = img['src']
                    if img_uri[0] != '/':
                        img_uri = '/'+img_uri
                    s.sendall(('GET ' + img_uri + ' HTTP/1.1\r\nHost: %s\r\n\r\n' % host.split("/",1)[0]).encode())
                    _, image_data =  recv_all(s)
                    
                    # save image
                    with open(path + '\\image_{}.png'.format(i), 'wb') as image_file:
                        image_file.write(image_data)
                        image_file.close()
                    img['src'] = img['src'].replace(img_uri, path + '\\image_{}.png'.format(i))
                    i += 1
                except:
                    print(img)
            f.close()
        
        with open(path + '\\index.html', 'w') as f:
            f.write(str(soup))
        s.close()
        
def headRequest(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        hostSplit = splitHost(host)[0]
        s.connect((hostSplit, port))
        headers = '{"If-Modified-Since": "Wed, 21 Oct 2015 07:28:00 GMT"}'
        request =  'HEAD ' + getUrl(host) + " HTTP/1.1\r\nHost: %s\r\n\r\n " % hostSplit + json.dumps(headers)
        s.sendall(request.encode())
        data = recv_all(s)
        path = createPaths(host) 

        with open(path + '\\index_head.html','wb') as f:
            f.write(data[0])
        s.close
        
def putRequest(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        hostSplit = splitHost(host)[0]
        s.connect((hostSplit, port))
        data = input("Give the string you want to place in a new file: ")
        url = getUrl(host) + "?data='" +data+ "'"
        request =  'PUT ' + url + " HTTP/1.1\r\nHost: %s\r\n\r\n" % hostSplit 
        s.send(request.encode())
        response = s.recv(1024)
        print(response)

def postRequest(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        hostSplit = splitHost(host)[0]
        s.connect((hostSplit, port))
        data = input("Give the string you want to append to a file: ")
        url = getUrl(host) + "?data='" +data + "'"
        request =  'POST ' + url + " HTTP/1.1\r\nHost: %s\r\n\r\n" % hostSplit 
        s.send(request.encode())
        response = s.recv(1024)
        print(response)

def main(argv):
    try:
        COMMAND = argv[0] # The command used for the HTTP request
        HOST = argv[1]  # The server's hostname or IP address
        PORT = int(argv[2])  # The port used by the server
        print('HTTP Command: ', argv[0])
        print('SERVER: ', argv[1])
        print('PORT: ', argv[2])

    except:
        print('Three arguments needed')
        sys.exit(2)
    
    if COMMAND == 'GET':
        getRequest(HOST, PORT)
    elif COMMAND == 'HEAD':
        headRequest(HOST, PORT)
    elif COMMAND == 'PUT':
        putRequest(HOST, PORT)
    elif COMMAND == 'POST':
        postRequest(HOST, PORT)
    else:
        print('Invalid commands given.')
        print('arg1: HTTP Command')
        print('arg2: HOST')
        print('arg3: Port')
     
        sys.exit(2)

if __name__ == "__main__":
   main(sys.argv[1:])