from base64 import encode
from fileinput import filename
from runpy import _ModifiedArgv0
import socket
from os.path import exists
from datetime import date
import re
from pathlib import Path
import os
def getRequest(connection, request):
    
    return 0

def headRequest(connection, request):
    return 0

def postRequest(connection, request):   
    path = getPath(request)
    print(path)
    if exists( path + '.txt'):
        file = open( path + '.txt', 'a')
        data = request.header.data
        file.write(data)
        connection.send(("200 Ok \n" + getDate()).encode())
    else:
        connection.send(BadRequest400())
   
    connection.close()
    

def putRequest(connection, request):
    path = getPath(request)
    with open(path,'w') as f:
            data = request.header.data
            f.write(str(data))
    
    connection.send(Ok200())
    connection.close()
    
        
def createPaths(path):
    final_path = os.path.join(os.getcwd(), path)
    if not os.path.isdir(final_path):
        print("making dir: " + final_path)
        os.makedirs (final_path,mode=0o777, exist_ok=False)
    return final_path
        
        
def getPath(request):
    fullPath = str(request).split("\n",2)[1].split(" ",1)[1]
    return createPaths(os.path.join("server", os.path.split(fullPath)[0]))
    
def checkModifiedSinceHeader(connection, request):
    field =request.header.If-Modified-Since
    print(field)
    return 0 

def Ok200():
    return ("200 Ok \n" + getDate() + "\n" + getContentType + "\n" + getContentLength).encode()

def NotModified304():
    return ("304 Not Modified \n" + getDate()).encode()

def BadRequest400():    
    return ("400 Bad Request \n" + getDate()).encode()

def NotFound404():
    return ("404 Not Found \n" + getDate()).encode()

def ServerError500():
    return ("500 Server Error \n" + getDate()).encode()


def getDate():
    return "Date: " + str(date.today())

def getContentType():
    return "Content-Type: text/"

def getContentLength():
    return str(6)



s = socket.socket()
print ("Socket successfully created")

port = 80

s.bind(('', port))
print ("socket binded to %s" %(port))

s.listen(5)
print ("socket is listening")

while True:
    connection, addr = s.accept()
    print ('Got connection from', addr )

    connection.send('Thank you for connecting'.encode())

    request = connection.recv(1024).decode()
    
    datasplit = str(request).split(" ",1)
    requestType = datasplit[0]
    
    if requestType == 'GET':
        getRequest(connection, request)
    elif requestType == 'HEAD':
        headRequest(connection, request)
    elif requestType == 'PUT':
        putRequest(connection, request)
    elif requestType == 'POST':
        postRequest(connection, request)

