import socket
from os.path import exists

def getRequest(connection, uri):
    print("connection: " + connection + "  uri: " + uri)


def headRequest(connection, uri):
    print("connection: " + connection + "  uri: " + uri)


def postRequest(connection, uri, data):
    if exists(uri):
        file = open(uri + '.txt', 'a')
        file.write(data)
        connection.send('200 Ok')
    else:
        connection.send('404 Not Found')
   
    connection.close()


def putRequest(connection, uri, data):
    print("connection: " + str(connection) + "  uri: " + uri + " data: " + data)
    with open(uri + '.html','w') as f:
            f.write(str(data))
    
    connection.send('200 Ok')
    connection.close()


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

