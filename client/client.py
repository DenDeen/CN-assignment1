#!/usr/bin/python

from bs4 import BeautifulSoup
import sys
import select
import socket
import stringProcessingClient

# 1. Fetches content length (or not if chunked)
# 2. Receives and appends the chunks
# 3. Returns decoded header and body
def recv_all(sock):
    chunks = b''

    # Receive header information
    chunk = sock.recv(2048)
    chunks += chunk

    # Get content length
    contentLength = stringProcessingClient.getContentLength(chunk)

    if (contentLength <= 2048):
        # Timeout of 3 seconds
        while select.select([sock], [], [], 3)[0]:
            data = sock.recv(2048)
            if not data: 
                break
            chunks += data
    else:
        counter = 2048

        # Receive from socket until the amount of bytes received becomes more than contentLength
        while counter < contentLength:
            chunk = sock.recv(2048)
            chunks += chunk
            counter += len(chunk)

    # Split headers and body
    headers_data = chunks.split(b'\r\n\r\n')[0]
    html_data = chunks[len(headers_data)+4:]
    return headers_data, html_data 

# 1. Sends GET request to host to receive html data
# 2. Sends GET requests for images in data, saves them and replaces the sources in html data
# 3. Stores the modified data in folder with host name
def getRequest(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Get host out of URI and connect
        hostSplit = host.split("/",1)[0]
        s.connect((hostSplit, port))

        # Add headers to request and send
        modifiedSinceHeader = "\r\nIf-Modified-Since: Wed, 21 Oct 2015 07:28:00 GMT"
        request = 'GET ' + stringProcessingClient.getUrl(host) +" HTTP/1.1\r\nHost: %s" % hostSplit 
        request += modifiedSinceHeader + "\r\n\r\n"
        s.sendall(request.encode())
        _, html_data = recv_all(s)

        # Create directory if it doesn't exist and create new file with fetched data
        path = stringProcessingClient.createPaths(host) 
        with open(path + '\\index.html','wb') as f:
            f.write(html_data)

        # Initialize parser over created html file
        soup = ''
        with open(path + '\\index.html') as f:
            soup = BeautifulSoup(f, "html.parser")
            i = 1

            # Find all images and send requests to host to store them on client
            for img in soup.find_all("img"):
                try:
                    # Fetch image
                    img_uri = img['src']
                    if img_uri[0] != '/':
                        img['src'] = img['src'].replace(img_uri, '/'+img_uri)
                        img_uri = '/'+img_uri
                    s.send(('GET ' + img_uri + ' HTTP/1.1\r\nHost: %s\r\n\r\n' % host.split("/",1)[0]).encode())
                    _, image_data =  recv_all(s)
                    
                    # Save image
                    with open(path + '\\image_{}.png'.format(i), 'wb') as image_file:
                        image_file.write(image_data)
                        image_file.close()

                    # Change src in html
                    img['src'] = img['src'].replace(img_uri, path + '\\image_{}.png'.format(i))
                    i += 1
                except:
                    print(img)
            f.close()
        
        # Store modified data
        with open(path + '\\index.html', 'w') as f:
            f.write(str(soup))
        s.close()

# 1. Sends HEAD request to host to receive header information
# 2. Stores the data in folder with host name
def headRequest(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Get host out of URI and connect
        hostSplit = host.split("/",1)[0]
        s.connect((hostSplit, port))

        # Add headers to request and send
        modifiedSinceHeader = "\r\nIf-Modified-Since: Wed, 21 Oct 2015 07:28:00 GMT"
        request = 'HEAD ' + stringProcessingClient.getUrl(host) +" HTTP/1.1\r\nHost: %s" % hostSplit 
        request += modifiedSinceHeader + "\r\n\r\n"
        s.send(request.encode())
        data = recv_all(s)

        # Create directory if it doesn't exist and create new file with fetched header
        path = stringProcessingClient.createPaths(host) 
        with open(path + '\\index_head.html','wb') as f:
            f.write(data[0])
        s.close

# 1. Sends PUT request to server
# 2. Requests input to place in new file on server
def putRequest(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Get host out of URI and connect
        hostSplit = host.split("/",1)[0]
        s.connect((hostSplit, port))

        # Ask string to insert in file and send
        data = input("Give the string you want to place in a new file: ")
        url = stringProcessingClient.getUrl(host) + "?data='" +data+ "'"
        request =  'PUT ' + url + " HTTP/1.1\r\nHost: %s\r\n\r\n" % hostSplit 
        s.send(request.encode())
        response = s.recv(1024)
        print(response)

# 1. Sends POST request to server
# 2. Requests input to append to file on server
def postRequest(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Get host out of URI and connect
        hostSplit = host.split("/",1)[0]
        s.connect((hostSplit, port))

        # Ask string to append to existing file and send
        data = input("Give the string you want to append to a file: ")
        url = stringProcessingClient.getUrl(host) + "?data='" +data + "'"
        request =  'POST ' + url + " HTTP/1.1\r\nHost: %s\r\n\r\n" % hostSplit 
        s.send(request.encode())
        response = s.recv(1024)
        print(response)

def main(argv):
    try:
        COMMAND = argv[0] # Request type
        HOST = argv[1]  # Hostname or IP address
        if(len(argv)>2):
            PORT = int(argv[2])  # Port used by server
        else:
            PORT = 80
        print('HTTP Command: ', COMMAND)
        print('SERVER: ', HOST)
        print('PORT: ', PORT)

    except Exception as e:
        print(e)
        print('Three arguments needed')
        sys.exit(2)
    
    # Navigate to right function depended on requestType
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