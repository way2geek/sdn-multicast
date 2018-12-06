import time
import socket

UDP_IP = "192.168.0.153"
UDP_PORT = 6767
MESSAGE = "Hola!"


while True:
    print "\n \t UDP target IP:", UDP_IP
    print "\t UDP target port:", UDP_PORT
    print "\t message:", MESSAGE

    sock = socket.socket(socket.AF_INET, # Internet
                            socket.SOCK_DGRAM) # UDP
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
    time.sleep(2)
