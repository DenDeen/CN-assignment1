#!/usr/bin/python

import socket
from datetime import datetime, date
import os
import socket
from _thread import *
import threading

print_lock = threading.Lock()

def formatFile(file):
    file = file.split('?')[0]
    return file.lstrip('/')

def getRequest(connection, requestFile, headers):   
    file = formatFile(requestFile)
    try:
        if file == '' or file[-1] == "/":
            file += "index.html"
        path =os.path.join("server",file) 
        file = open(path,'rb') 
        
        if("If-Modified-Since: " in headers): 
            modifiedSince = headers.split("If-Modified-Since: ",1)[1].split("\r\n",1)[0]
            datetime_object = datetime.strptime(modifiedSince, '%a, %d %b %Y %X %Z')
            if  datetime.timestamp(datetime_object) > os.path.getctime(path):
                header = 'HTTP/1.1 304 NOT MODIFIED'
                response = b""
            else:
                response = file.read()
                file.close()

                header = 'HTTP/1.1 200 OK\n'
                ContentType = getContentType(path)
                header += 'Content-Type: '+str(ContentType)+ '\n' + getDate() + " \n" + "Content-length: " + str(len(response))

        else:
            response = file.read()
            file.close()

            header = 'HTTP/1.1 200 OK\n'
            ContentType = getContentType(path)
            header += 'Content-Type: '+str(ContentType)+ '\n' + getDate() + " \n" + "Content-length: " + str(len(response))

       
    
    except Exception as e:
        print(e)
        header = 'HTTP/1.1 404 Not Found\n\n ' 
        response = '<html><body><center><h3>Error 404: File not found</h3></center></body></html>'.encode('utf-8')

    final_response = header.encode('utf-8')
    final_response += b'\r\n\r\n'
    final_response += response 
    connection.send(final_response)

def headRequest(connection, requestFile, headers):
    file = formatFile(requestFile)
    try:
        if file[-1] == "/" or file == '':
            file += "index.html"
        path =os.path.join("server",file) 
        file = open(path,'rb') 
        if("If-Modified-Since: " in headers): 
            modifiedSince = headers.split("If-Modified-Since: ",1)[1].split("\r\n",1)[0]
            datetime_object = datetime.strptime(modifiedSince, '%a, %d %b %Y %X %Z')
            if  datetime.timestamp(datetime_object) > os.path.getctime(path):
                header = 'HTTP/1.1 304 NOT MODIFIED'
            else:
                fileLength = str(len(file.read()))
                file.close()

                header = 'HTTP/1.1 200 OK\n'
                ContentType = getContentType(path)
                header += 'Content-Type: '+str(ContentType)+ '\n' + getDate() + " \n" + "Content-length: " + fileLength

        else:
            fileLength = str(len(file.read()))
            file.close()

            header = 'HTTP/1.1 200 OK\n'
            ContentType = getContentType(path)
            header += 'Content-Type: '+str(ContentType)+ '\n' + getDate() + " \n" + "Content-length: " + fileLength
       
    except Exception as e:
        print(e)
        header = 'HTTP/1.1 404 Not Found\n\n'
        
    connection.send(header.encode('utf-8'))

def postRequest(connection, requestFile, request):  
    file = formatFile(requestFile)
    data = request.split("?data='",1)[1].split("'")[0]
    
    if file == '/' or file == '':
        header = 'HTTP/1.1 400 Bad request\n\n'
    else:
        try:
            if(file.endswith(".txt")):
                createPaths(file)
                path = os.path.join("server",file)
                if os.path.exists(path):
                    file = open(path,'a')
                    file.write("\n")
                else:
                    file = open(path,'a')
                file.write(data)
                file.close()
                header = 'HTTP/1.1 200 OK\n'
            else:
                header = 'HTTP/1.1 400 Bad request\n\n'
                
        except Exception as e:
            print(e)
            header = 'HTTP/1.1 500 Server error\n\n'
    
    final_response = header.encode('utf-8')
    connection.send(final_response)

def putRequest(connection, requestFile, request):
    file = formatFile(requestFile)
    data = request.split("?data='",1)[1].split("'")[0]
    
    if file == '/' or file == '':
        print("hallo")
        header = 'HTTP/1.1 400 Bad request\n\n'
    else:
        try:
            if(file.endswith(".txt")):
                createPaths(file)
                path =os.path.join("server",file) 
                file = open(path,'w') 
                file.write(data)
                file.close()

                header = 'HTTP/1.1 200 OK\n'
            else:
                header = 'HTTP/1.1 400 Bad request\n\n'
                
        except Exception as e:
            print(e)
            header = 'HTTP/1.1 500 Server error\n\n'
    
    final_response = header.encode('utf-8')
    connection.send(final_response)

def createPaths(file):
    path = os.path.join(os.getcwd(),os.path.join("server", os.path.split(file)[0]))
    if not os.path.isdir(path):
        print("making dir: " + path)
        os.makedirs (path,mode=0o777, exist_ok=False)
    return path

def getPath(request):
    fullPath = str(request).split("\n",2)[1].split(" ",1)[1]
    return os.path.join(os.getcwd(),os.path.join("server", os.path.split(fullPath)[0]))

def getDate():
    return "Date: " + str(date.today())

def getContentType(path):
    if(path.endswith(".jpg")):
        return 'image/jpg'
    elif(path.endswith(".css")):
        return 'text/css'
    else:
        return 'text/html'

def threaded(connection):
    listen = True
    while listen:
        request = connection.recv(1024).decode()
        if(request == ""):
            listen = False
        else:
            datasplit = str(request).split(" ",2)
            requestType = datasplit[0]
            requestFile = datasplit[1]
            header = datasplit[2]
        
            if "Host: " in header:
                if requestType == 'GET':
                    getRequest(connection, requestFile, header)
                elif requestType == 'HEAD':
                    headRequest(connection, requestFile, header)
                elif requestType == 'PUT':
                    putRequest(connection, requestFile, request)
                elif requestType == 'POST':
                    postRequest(connection, requestFile, request)
            else:
                connection.send('HTTP/1.1 400 Bad request\n\n'.encode())
    print("closing thread and connection: " + str(connection))
    connection.close()
    exit() 

def main(): 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print ("Socket successfully created")

    port = 80

    s.bind(('', port))
    print ("socket binded to %s" %(port))

    s.listen(5)
    print ("socket is listening")

    while True:
        connection, _ = s.accept()
        start_new_thread(threaded,(connection,))
        print("New connection made")        

if __name__ == "__main__":
   main()
