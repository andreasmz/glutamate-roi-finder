import imagej
from scyjava import jimport

ij = None

def Init():
    global ij
    ij = imagej.init('C:\\Users\\abril\\Andreas Eigene Dateien\\Programme\\Fiji.app', mode='interactive')
    print(type(ij))

def Show():
    ij.ui().showUI()
    print("Zeige dich!")