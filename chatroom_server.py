# -*- coding: utf-8 -*-
"""
Created on Wed May  1 13:38:39 2024

@author: Samuele
"""

# Server della chatroom

import socket, threading

# funzione per gestire il generico client, diventerà un thread
def handle_client(user, addr):
    print(f"[thread] client {addr} connected")
    user.send("Your name:".encode('utf-8'))
    # registro socket e nickname
    nickname = user.recv(1024).decode('utf-8')
    connections[user] = nickname
    # messaggio personalizzato per il client
    user.send("You joined the chat".encode('utf-8'))
    # notifica per ogni altro utente che un nuovo client è entrato
    broadcast(f"{nickname} joined the chat", user, noName = True)
    while True:
        # msg deve essere inizializzato fuori dal try, altrimenti
        # non è visisbile a r.39
        msg = ""
        try:
            # ricevo ogni eventuale messaggio dal client
            msg = user.recv(1024).decode('utf-8')
            if msg == "{quit}":
                raise KeyboardInterrupt
        except:
            broadcast(f"{connections[user]} has left the chat", user, noName = True)
            del connections[user]
            # in caso di chiusura della connessione da parte del client:
            print(f"[thread] client {addr} disconnected")
            user.close()
            break
        # se non viene lanciata nessuna eccezione, invio il messaggio
        # a tutti i membri della chatroom
        broadcast(msg, user)

# funzione per trasmettere il messaggio a tutti gli utenti
def broadcast(msg, user = None, noName = False):
        # per ogni utente connesso
        for usr in connections.keys():
            if usr != user:
                if noName:
                    usr.send(msg.encode('utf-8'))
                else:
                    # viene inviato il messaggio formattato
                    usr.send(f"{connections[user]}: {msg}".encode('utf-8'))

def close_routine():
    for client in connections.keys():
        client.send("{shutdown}".encode('utf-8'))

# per convenzione scelgo la porta 8080
port = 8080
# creazione server TCP
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', port))
# setto un timeout sul socket del server per far si che possa rispondere
# ad un interrupt da tastiera anche mentre è bloccato nella accept()
server.settimeout(0.5)
server.listen(1)

# dictionary dove ad ogni client-socket è associato un nickname
# al momento della connessione
connections = {}

print("ready to serve...")
try:
    while True:
        try:
            # accetto la connessione e chiedo il nickname
            user, address = server.accept()
            # apro un processo per gestire questo client e ritorno in ascolto
            threading.Thread(target=handle_client, args=((user, address))).start()
        except KeyboardInterrupt:
                # il key board interrupt deve passare fuori dal while true
                pass
        except socket.timeout:
                pass
except KeyboardInterrupt:
    # attuo la close routine per avvisare ogni client che
    # il server è stato chiuso
    close_routine()
    # una volta fuori dal ciclo chiudo il server
    server.close()
    print("server shutdown.")