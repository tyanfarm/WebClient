from threading import Thread
import threading
from connection import MultipleConnection
from connection import ClientConnection
from inputLink import inputLink

websiteList = inputLink()
MultipleConnection(websiteList)

# try:
#     for i in websiteList:
#         t = threading.Thread(target = ClientConnection, args = (i, ))
#         t.start()
# except:
#     print('ERROR')

