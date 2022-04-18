from base64 import encode
import socket
from os.path import exists
from datetime import date

def getRequest(connection, uri):
    getFile()
    #Todo file doorsturen, en via request kijken naar welke file er gezocht wordt


def headRequest(connection, uri):
    getFile()
    #Todo file doorsturen, en via request kijken naar welke file er gezocht wordt
    #Enkel de head sturen



def postRequest(connection, uri, data):
    #Kijken welke content-type er wordt doorgestuurd in de request
    if exists(uri + '.txt'):
        file = open(uri + '.txt', 'a')
        file.write(data)
        connection.send(Ok200())
    else:
        connection.send(BadRequest400())
   
    connection.close()


def putRequest(connection, uri, data):
    #Kijken welke content type
    print("connection: " + str(connection) + "  uri: " + uri + " data: " + data)
    with open(uri + '.txt','w') as f:
            f.write(str(data))
    
    connection.send(Ok200())
    connection.close()

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
    uri = datasplit[1]
    
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
