from base64 import encode
from runpy import _ModifiedArgv0
import socket
from os.path import exists
from datetime import date

def getRequest(connection, request):
    
    return 0

def headRequest(connection, request):
    return 0

def postRequest(connection, request):
    if exists( + '.txt'):
        file = open( + '.txt', 'a')
        data = request.header.data
        file.write(data)
        connection.send(("200 Ok \n" + getDate()).encode())
    else:
        connection.send(BadRequest400())
   
    connection.close()


def putRequest(connection, request):
    with open( + '.txt','w') as f:
            data = request.header.data
            f.write(str(data))
    
    connection.send(Ok200())
    connection.close()

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
    
    print("requestType: " + requestType)
    print("request")
    if requestType == 'GET':
        getRequest(connection, request)
    elif requestType == 'HEAD':
        headRequest(connection, request)
    elif requestType == 'PUT':
        putRequest(connection, request)
    elif requestType == 'POST':
        postRequest(connection, request)

    print(request)

