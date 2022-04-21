import re
import os

def getContentCharset(head):
    try:
        result = re.search(b'charset=(.*?)\\r', head)
        return result.group(1).decode("utf-8")
    except:
        return 'unicode_escape'

def getContentLength(head):
    try:
        result = re.search(b'Content-Length:(.*?)\\r', head)
        return int(result.group(1).decode("utf-8"))
    except:
        return 2048

def getHost(host):
    result = re.search('(?<=\.).*(?=\.)', host.split('/')[0]).group(0)
    if (result == '0.0'):
        return 'localhost'
    else:
        return result

def splitHost(host):
    return host.split("/",1)    

def getUrl(host):
    if len(splitHost(host)) > 1:
        return splitHost(host)[1]
    else:
        return "/"
    
def createPaths(file):
    path = os.path.join(os.getcwd(),os.path.join("client", getHost(file)))
    if not os.path.isdir(path):
        print("making dir: " + path)
        os.makedirs (path, mode=0o777, exist_ok=False)
    return path