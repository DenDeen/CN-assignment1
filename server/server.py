from base64 import encode
import socket
from os.path import exists
from datetime import date

def getRequest(connection, uri):
    
    return 0

def headRequest(connection, uri):
    return 0

def postRequest(connection, uri, data):
    if exists(uri + '.txt'):
        file = open(uri + '.txt', 'a')
        file.write(data)
        connection.send(("200 Ok \n" + getDate()).encode())
    else:
        connection.send(BadRequest400())
   
    connection.close()


def putRequest(connection, uri, data):
    print("connection: " + str(connection) + "  uri: " + uri + " data: " + data)
    with open(uri + '.txt','w') as f:
            f.write(str(data))
    
    connection.send(Ok200())
    connection.close()

def checkModifiedSinceHeader(connection, uri):
    
    return 0 

def getFile():
    #Error handeling
    if exists(uri + '.txt'):
        return open(uri + '.txt', 'a')
    elif exists(uri + '.html'):
        return open(uri + '.html', 'a')

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
    
    datasplit = str(request).split(" ",2)
    requestType = datasplit[0]
    
    
    print("requestType: " + requestType)
    
    if requestType == 'GET':
        getRequest(connection, uri)
    elif requestType == 'HEAD':
        headRequest(connection, uri)
    elif requestType == 'PUT':
        putRequest(connection, uri, datasplit[2])
    elif requestType == 'POST':
        postRequest(connection, uri, datasplit[2])

    print(request)

