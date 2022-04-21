#!/usr/bin/python

import socket
import os
import socket
import stringProcessingServer
from _thread import *
from datetime import datetime

# HTTP Get Request
def getRequest(connection, requestFile, headers):   
    file = stringProcessingServer.formatFile(requestFile)
    try:
        # Get index.html if path ends on /
        if file == '' or file[-1] == "/":
            file += "index.html"
            
        # Add server to file path    
        path =os.path.join("server",file) 
        file = open(path,'rb') 

        if("If-Modified-Since: " in headers):
            # Get date and convert it to proper format
            modifiedSince = headers.split("If-Modified-Since: ",1)[1].split("\r\n",1)[0]
            datetime_object = datetime.strptime(modifiedSince, '%a, %d %b %Y %X %Z')

            # If data after last modification return 304, 
            # otherwise return 200 and content
            if  datetime.timestamp(datetime_object) > os.path.getctime(path):
                header = 'HTTP/1.1 304 NOT MODIFIED'
                response = b""
            else:
                response = file.read()
                file.close()
                
                header = 'HTTP/1.1 200 OK\n'
                ContentType = stringProcessingServer.getContentType(path)
                header += 'Content-Type: '+str(ContentType)+ '\n' + stringProcessingServer.getDate() + " \n" + "Content-length: " + str(len(response))

        else:
            response = file.read()
            file.close()
            
            header = 'HTTP/1.1 200 OK\n'
            ContentType = stringProcessingServer.getContentType(path)
            header += 'Content-Type: '+str(ContentType)+ '\n' + stringProcessingServer.getDate() + " \n" + "Content-length: " + str(len(response))

    except Exception as e:
        print(e)
        header = 'HTTP/1.1 404 Not Found\n\n ' 
        response = '<html><body><center><h3>Error 404: File not found</h3></center></body></html>'.encode('utf-8')
        
    # Return response to client
    final_response = header.encode('utf-8')
    final_response += b'\r\n\r\n'
    final_response += response 
    connection.send(final_response)
    
# HTTP Head Request
def headRequest(connection, requestFile, headers):
    file = stringProcessingServer.formatFile(requestFile)
    try:
        # Get index.html if path ends on /
        if file[-1] == "/" or file == '':
            file += "index.html"
        
        # Add server to file path    
        path =os.path.join("server",file) 
        file = open(path,'rb') 
        if("If-Modified-Since: " in headers):
            # Get the date and convert it
            modifiedSince = headers.split("If-Modified-Since: ",1)[1].split("\r\n",1)[0]
            datetime_object = datetime.strptime(modifiedSince, '%a, %d %b %Y %X %Z')
            
            # If data after last modification return 304, 
            # otherwise return 200 and content
            if  datetime.timestamp(datetime_object) > os.path.getctime(path):
                header = 'HTTP/1.1 304 NOT MODIFIED'
            else:
                fileLength = str(len(file.read()))
                file.close()

                header = 'HTTP/1.1 200 OK\n'
                ContentType = stringProcessingServer.getContentType(path)
                header += 'Content-Type: '+str(ContentType)+ '\n' + stringProcessingServer.getDate() + " \n" + "Content-length: " + fileLength

        else:
            fileLength = str(len(file.read()))
            file.close()

            header = 'HTTP/1.1 200 OK\n'
            ContentType = stringProcessingServer.getContentType(path)
            header += 'Content-Type: '+str(ContentType)+ '\n' + stringProcessingServer.getDate() + " \n" + "Content-length: " + fileLength
       
    except Exception as e:
        print(e)
        header = 'HTTP/1.1 404 Not Found\n\n'
        
    # Return response to client 
    connection.send(header.encode('utf-8'))
    
# HTTP POST Request
def postRequest(connection, requestFile, request):
    # Format file and split data from request
    file = stringProcessingServer.formatFile(requestFile)
    data = request.split("?data='",1)[1].split("'")[0]
    
    # Return Bad request if there isnt a file name at the end of the path
    if file == '/' or file == '':
        header = 'HTTP/1.1 400 Bad request\n\n'
    else:
        try:
            # Only allow .txt files
            if(file.endswith(".txt")):   
                # Create paths to the new file and format path
                stringProcessingServer.createPaths(file)
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
    
    # Return response header
    final_response = header.encode('utf-8')
    connection.send(final_response)

# HTTP Put Request
def putRequest(connection, requestFile, request):
    # Format file and split data from request
    file = stringProcessingServer.formatFile(requestFile)
    data = request.split("?data='",1)[1].split("'")[0]
    
    # Return Bad request if there isnt a file name at the end of the path
    if file == '/' or file == '':
        header = 'HTTP/1.1 400 Bad request\n\n'
    else:
        try:
            # Only allow .txt files
            if(file.endswith(".txt")):

                # Create paths to the new file and format path
                stringProcessingServer.createPaths(file)
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
            
    # Return response to client
    final_response = header.encode('utf-8')
    connection.send(final_response)

# Multithreading support
def threaded(connection):
    while True:
        request = connection.recv(1024).decode()

        # Close the connection and the thread if request is empty
        if(request == ""):
            break
        else:
            # Split the request into requestType, requested file(uri), and headers
            datasplit = str(request).split(" ",2)
            requestType = datasplit[0]
            requestFile = datasplit[1]
            header = datasplit[2]
            
            # Navigate to right function depended on requestType
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
                # If requestType isn't supported, return 400 bad request
                connection.send('HTTP/1.1 400 Bad request\n\n'.encode())
                
    # Send timeout header to client and close connection and thread            
    print("closing thread and connection: " + str(connection))
    connection.send('HTTP/1.1 408 Request Timeout\n\n'.encode('utf-8'))
    connection.close()
    exit() 

# Start main function
def main(): 
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print ("Socket successfully created")

    port = 80

    s.bind(('', port))
    print ("socket binded to %s" %(port))

    s.listen(5)
    print ("socket is listening")

    # Accepting incomming connections, and make a new thread for them
    while True:
        connection, _ = s.accept()
        
        start_new_thread(threaded,(connection,))
        print("New connection made")        

if __name__ == "__main__":
   main()
