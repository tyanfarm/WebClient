from threading import Thread
import threading
from connection import MultipleConnection
from inputLink import inputLink

websiteList = inputLink()

try:
    t = threading.Thread(target = MultipleConnection, args = (websiteList, ))
    t.start()
except:
    print('ERROR')

