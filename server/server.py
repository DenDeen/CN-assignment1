from base64 import encode
from fileinput import filename
from runpy import _ModifiedArgv0
import socket
from os.path import exists
from datetime import datetime, date
import re
from pathlib import Path
import os
from venv import create
import json

def getRequest(connection, requestFile, headers):
    file = requestFile.split('?')[0]
    file = file.lstrip('/')

    if(file == '/'):
        file = 'server/index.html'
    
    try:
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

                if(path.endswith(".jpg")):
                    mimetype = 'image/jpg'
                elif(path.endswith(".css")):
                    mimetype = 'text/css'
                else:
                    mimetype = 'text/html'

                header += 'Content-Type: '+str(mimetype)+ '\n' + getDate() + " \n" + "Content-length: " + str(len(response))

        else:
            response = file.read()
            file.close()

            header = 'HTTP/1.1 200 OK\n'

            if(path.endswith(".jpg")):
                mimetype = 'image/jpg'
            elif(path.endswith(".css")):
                mimetype = 'text/css'
            else:
                mimetype = 'text/html'

            header += 'Content-Type: '+str(mimetype)+ '\n' + getDate() + " \n" + "Content-length: " + str(len(response))

        final_response = header.encode('utf-8')
        final_response += b'\r\n\r\n'
        final_response += response 
        connection.send(final_response)
        connection.close()
    
    except Exception as e:
        print(e)
        header = 'HTTP/1.1 404 Not Found\n\n ' 
        response = '<html><body><center><h3>Error 404: File not found</h3></center></body></html>'.encode('utf-8')

    
        
    
def headRequest(connection, requestFile, headers):
    file = requestFile.split('?')[0]
    file = file.lstrip('/')

    if(file == '/'):
        file = 'server/index.html'
    
    try:
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

                if(path.endswith(".jpg")):
                    mimetype = 'image/jpg'
                elif(path.endswith(".css")):
                    mimetype = 'text/css'
                else:
                    mimetype = 'text/html'

                header += 'Content-Type: '+str(mimetype)+ '\n' + getDate() + " \n" + "Content-length: " + fileLength

        else:
            fileLength = str(len(file.read()))
            file.close()

            header = 'HTTP/1.1 200 OK\n'

            if(path.endswith(".jpg")):
                mimetype = 'image/jpg'
            elif(path.endswith(".css")):
                mimetype = 'text/css'
            else:
                mimetype = 'text/html'

            header += 'Content-Type: '+str(mimetype)+ '\n' + getDate() + " \n" + "Content-length: " + fileLength
            
        connection.send(header.encode('utf-8'))
        connection.close()
       
    except Exception as e:
        print(e)
        header = 'HTTP/1.1 404 Not Found\n\n'
        
    
    

def postRequest(connection, requestFile, request):  
    file = requestFile.split('?')[0]
    file = file.lstrip('/')
    data = request.split("?data='",1)[1].split("'")[0]
    
    if(file == '/'):
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
    connection.close()
        

def putRequest(connection, requestFile, request):
    file = requestFile.split('?')[0]
    file = file.lstrip('/')
    data = request.split("?data='",1)[1].split("'")[0]
    
    if(file == '/'):
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
    connection.close()
    
        
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


s = socket.socket()
print ("Socket successfully created")

port = 80

s.bind(('', port))
print ("socket binded to %s" %(port))

s.listen(5)
print ("socket is listening")

while True:
    connection, addr = s.accept()

    request = connection.recv(1024).decode()
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
        connection.close()

