# -*- coding: utf-8 -*-
"""
Created on Wed May  1 14:47:51 2024

@author: Samuele
"""


# Client della chatroom

import time, socket, threading

# metodo che viene eseguito in un thread per mostrare i messaggi degli
# altri utenti in tempo reale
def receive(client, stop_flag):
    while not stop_flag:
        try:
            # stampo ogni messaggio ricevuto dal server
            msg = client.recv(1024).decode('utf-8')
            if msg == "{shutdown}":
                client.close()
                print("lost connection with the server")
                stop_flag = True
            else:
                print(msg)
        except socket.timeout:
            # intervallo di polling con cui controllo se
            # il client vuole interrompere la connessione
            pass
        except:
            break

# metodo eseguito alla creazione della connessione, permette al client
# di scrivere messaggi nella chatroom, mantiene anche il controllo della
# ricezione dei messaggi, in caso venisse interrotto, è write a gestire
# la procedura di chiusura lato client
def write(client, stop_flag):
    while not stop_flag:
        try:
            msg = input()
            client.send(msg.encode('utf-8'))
        except socket.timeout:
            pass
        except KeyboardInterrupt:
            # setting the condition for the read thread to stop
            stop_flag = True
        
port = 8080

# creazione socket e tentativo di connessione
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connected = True
try:
    client_socket.connect(('localhost', port))
except:
    print(f"There's no server active at {'localhost'} on port {port}")
    connected = False
if connected:
    client_socket.settimeout(0.5)
    stop = False
    # la ricezione dei messaggi eseguirà su un thread separato
    r = threading.Thread(target=receive, args=((client_socket, stop)))
    r.start()
    # il processo di scrittura invece verrà gestito nel main
    write(client_socket, stop)
    print("you succesfully disconnected, thank you")
    # provo a chiudere la connessione, se non è già chiusa
    try:
        client_socket.send("{quit}".encode('utf-8'))
        client_socket.close()
    except:
        pass

time.sleep(1.5)