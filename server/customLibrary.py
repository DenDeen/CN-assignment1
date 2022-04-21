from datetime import date
import os

#Clean up file name
def formatFile(file):
    file = file.split('?')[0]
    return file.lstrip('/')

#Make directories and return the paths 
def createPaths(file):
    path = os.path.join(os.getcwd(),os.path.join("server", os.path.split(file)[0]))
    if not os.path.isdir(path):
        print("making dir: " + path)
        os.makedirs()
    return path

#Get a string of the date to return in the headers
def getDate():
    return "Date: " + str(date.today())

#Switch over the ending of the path to find the the content type
def getContentType(path):
    if(path.endswith(".jpg")):
        return 'image/jpg'
    elif(path.endswith(".css")):
        return 'text/css'
    else:
        return 'text/html'