#!/usr/bin/python

import socket
import os
import socket
import customLibrary
from _thread import *
from datetime import datetime

#HTTP Get Request
def getRequest(connection, requestFile, headers):   
    file = customLibrary.formatFile(requestFile)
    try:
        #If path ends on nothing, try to get index.html
        if file == '' or file[-1] == "/":
            file += "index.html"
            
        #Add server to file path    
        path =os.path.join("server",file) 
        file = open(path,'rb') 

        if("If-Modified-Since: " in headers): 
            #Get the date and convert it
            modifiedSince = headers.split("If-Modified-Since: ",1)[1].split("\r\n",1)[0]
            datetime_object = datetime.strptime(modifiedSince, '%a, %d %b %Y %X %Z')
            #See if datetime is after the date of the file last modification, if so return 304, otherwise return 200 and content
            if  datetime.timestamp(datetime_object) > os.path.getctime(path):
                header = 'HTTP/1.1 304 NOT MODIFIED'
                response = b""
            else:
                response = file.read()
                file.close()
                
                header = 'HTTP/1.1 200 OK\n'
                ContentType = customLibrary.getContentType(path)
                header += 'Content-Type: '+str(ContentType)+ '\n' + customLibrary.getDate() + " \n" + "Content-length: " + str(len(response))

        else:
            response = file.read()
            file.close()
            
            header = 'HTTP/1.1 200 OK\n'
            ContentType = customLibrary.getContentType(path)
            header += 'Content-Type: '+str(ContentType)+ '\n' + customLibrary.getDate() + " \n" + "Content-length: " + str(len(response))

    except Exception as e:
        print(e)
        header = 'HTTP/1.1 404 Not Found\n\n ' 
        response = '<html><body><center><h3>Error 404: File not found</h3></center></body></html>'.encode('utf-8')
        
    #Returns response to client
    final_response = header.encode('utf-8')
    final_response += b'\r\n\r\n'
    final_response += response 
    connection.send(final_response)
    
#HTTP Head Request
def headRequest(connection, requestFile, headers):
    file = customLibrary.formatFile(requestFile)
    try:
        #If path ends on nothing, try to get index.html
        if file[-1] == "/" or file == '':
            file += "index.html"
        
        #Add server to file path    
        path =os.path.join("server",file) 
        file = open(path,'rb') 
        if("If-Modified-Since: " in headers): 
            #Get the date and convert it
            modifiedSince = headers.split("If-Modified-Since: ",1)[1].split("\r\n",1)[0]
            datetime_object = datetime.strptime(modifiedSince, '%a, %d %b %Y %X %Z')
            #See if datetime is after the date of the file last modification, if so return 304, otherwise return 200 and content
            if  datetime.timestamp(datetime_object) > os.path.getctime(path):
                header = 'HTTP/1.1 304 NOT MODIFIED'
            else:
                fileLength = str(len(file.read()))
                file.close()

                header = 'HTTP/1.1 200 OK\n'
                ContentType = customLibrary.getContentType(path)
                header += 'Content-Type: '+str(ContentType)+ '\n' + customLibrary.getDate() + " \n" + "Content-length: " + fileLength

        else:
            fileLength = str(len(file.read()))
            file.close()

            header = 'HTTP/1.1 200 OK\n'
            ContentType = customLibrary.getContentType(path)
            header += 'Content-Type: '+str(ContentType)+ '\n' + customLibrary.getDate() + " \n" + "Content-length: " + fileLength
       
    except Exception as e:
        print(e)
        header = 'HTTP/1.1 404 Not Found\n\n'
        
    #Returns response to client 
    connection.send(header.encode('utf-8'))
    
#HTTP POST Request
def postRequest(connection, requestFile, request):  
    #format file and split data from request
    file = customLibrary.formatFile(requestFile)
    data = request.split("?data='",1)[1].split("'")[0]
    
    #return Bad request if there isnt a file name at the end of the path
    if file == '/' or file == '':
        header = 'HTTP/1.1 400 Bad request\n\n'
    else:
        try:
            #Only allow .txt files
            if(file.endswith(".txt")):
                #Create paths to the new file
                customLibrary.createPaths(file)
                #Add server to the relative path to the file
                path = os.path.join("server",file)
                #See if file already excist, if so add a new line before appending
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
    #return response header
    final_response = header.encode('utf-8')
    connection.send(final_response)

#HTTP Put Request
def putRequest(connection, requestFile, request):
    #format file and split data from request
    file = customLibrary.formatFile(requestFile)
    data = request.split("?data='",1)[1].split("'")[0]
    
    #return Bad request if there isnt a file name at the end of the path
    if file == '/' or file == '':
        header = 'HTTP/1.1 400 Bad request\n\n'
    else:
        try:
            #Only allow .txt files
            if(file.endswith(".txt")):
                #Create paths to the new file
                customLibrary.createPaths(file)
                #Add server to the relative path to the file
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
            
    #Return response to client
    final_response = header.encode('utf-8')
    connection.send(final_response)

#Function for threads
def threaded(connection):
    #Keep on getting new requests
    while True:
        request = connection.recv(1024).decode()
        #If there is an empty request, stop receiving, close the connection and the thread
        if(request == ""):
            break
        else:
            #Split the request into the requestType, the requested file(uri), and the headers
            datasplit = str(request).split(" ",2)
            requestType = datasplit[0]
            requestFile = datasplit[1]
            header = datasplit[2]
            
            #Check for all requests if the host header is in it
            if "Host: " in header:
                #Go over the requestType to get the correct handler function
                if requestType == 'GET':
                    getRequest(connection, requestFile, header)
                elif requestType == 'HEAD':
                    headRequest(connection, requestFile, header)
                elif requestType == 'PUT':
                    putRequest(connection, requestFile, request)
                elif requestType == 'POST':
                    postRequest(connection, requestFile, request)
            else:
                #If the requestType isn't one of the supported ones, return 400 bad request
                connection.send('HTTP/1.1 400 Bad request\n\n'.encode())
                
    #Send timeout header to client and close the connection and the thread            
    print("closing thread and connection: " + str(connection))
    connection.send('HTTP/1.1 408 Request Timeout\n\n'.encode('utf-8'))
    connection.close()
    exit() 

#Starts main function
def main(): 
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print ("Socket successfully created")

    port = 80

    s.bind(('', port))
    print ("socket binded to %s" %(port))

    s.listen(5)
    print ("socket is listening")

    #Keep on accepting incomming connections, and make a new thread for them
    while True:
        connection, _ = s.accept()
        
        start_new_thread(threaded,(connection,))
        print("New connection made")        

if __name__ == "__main__":
   main()
