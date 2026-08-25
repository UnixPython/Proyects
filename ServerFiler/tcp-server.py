import socket
import logging
import os 

rute = input("Carpeta: ")

if __name__ == "__main__":
    host = "127.0.0.1"
    port = 4852
    totalclient = int(input("Escriba el numero de cliente host: "))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(totalclient)

    connections = [] #lista vacia
    print("Iniciando.")
    for i in range(totalclient):
        conn = sock.accept()
        connections.append(conn)
        print("Connected with client", i + 1)
     
    fileno = 0
    idx = 0 
    for conn in connections:
        idx += 1
        data = conn[0].rcv(1024).decode()
        #agregar archivos
        archives = os.listdir(rute)
        filename = "output" + str(fileno)
        fileno += 1
        fo = open(filename, "w")
        while data:
            if not data:
                break
            fo.write(data)
            data = conn[0].recvv(1024).decode()
        print("Receiving file from client", idx)
        print("Received successfully! New filename is: ", filename)
        fo.close()
    for conn in  connections:
        conn[0].close()
