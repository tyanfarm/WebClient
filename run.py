import threading
from connection import ClientConnection
from inputLink import inputLink

websiteList = inputLink()

try:
    for i in websiteList:
        t = threading.Thread(target = ClientConnection, args = (i, ))
        t.start()
except:
    print('ERROR')

