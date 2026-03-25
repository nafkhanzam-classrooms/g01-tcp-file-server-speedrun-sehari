import socket
import select
import os

HOST = '127.0.0.1'
PORT = 5000
BUFFER_SIZE = 4096
SERVER_FOLDER = 'server_files'

if not os.path.exists(SERVER_FOLDER):
    os.makedirs(SERVER_FOLDER)

def broadcast(message, sender_sock, sockets_list):
    for sock in sockets_list:
        if sock != sender_sock and sock.fileno() != -1: # Jangan kirim ke server socket dan sender
            try:
                sock.sendall(message.encode('utf-8'))
            except:
                pass

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    
    sockets_list = [server]
    print(f"[LISTENING] Server-Select berjalan di {HOST}:{PORT}")
    
    while True:
        read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
        
        for notified_socket in read_sockets:
            if notified_socket == server:
                client_socket, client_address = server.accept()
                sockets_list.append(client_socket)
                print(f"[CONNECTED] {client_address} terhubung.")
            else:
                try:
                    data = notified_socket.recv(BUFFER_SIZE).decode('utf-8')
                    if not data:
                        print(f"[DISCONNECTED] Klien terputus.")
                        sockets_list.remove(notified_socket)
                        continue
                        
                    if data.startswith('CHAT|'):
                        msg = data.split('|', 1)[1]
                        broadcast(f"CHAT|Klien berkata: {msg}", notified_socket, [s for s in sockets_list if s != server])
                        
                    elif data.startswith('LIST|'):
                        files = os.listdir(SERVER_FOLDER)
                        file_list = ", ".join(files) if files else "Kosong"
                        notified_socket.sendall(f"CHAT|File di server: {file_list}".encode('utf-8'))
                        
                    elif data.startswith('UPLOAD|'):
                        parts = data.split('|')
                        filename = parts[1]
                        filesize = int(parts[2])
                        filepath = os.path.join(SERVER_FOLDER, filename)
                        
                        bytes_received = 0
                        with open(filepath, 'wb') as f:
                            while bytes_received < filesize:
                                chunk = notified_socket.recv(min(BUFFER_SIZE, filesize - bytes_received))
                                if not chunk: break
                                f.write(chunk)
                                bytes_received += len(chunk)
                        broadcast(f"CHAT|Seseorang mengupload {filename}", notified_socket, [s for s in sockets_list if s != server])
                        
                    elif data.startswith('DOWNLOAD|'):
                        filename = data.split('|')[1]
                        filepath = os.path.join(SERVER_FOLDER, filename)
                        if os.path.exists(filepath):
                            filesize = os.path.getsize(filepath)
                            notified_socket.sendall(f"FILE|{filename}|{filesize}".encode('utf-8'))
                            with open(filepath, 'rb') as f:
                                while (chunk := f.read(BUFFER_SIZE)):
                                    notified_socket.sendall(chunk)
                        else:
                            notified_socket.sendall(f"CHAT|Error: File tidak ditemukan.".encode('utf-8'))
                            
                except Exception as e:
                    print(f"[ERROR] {e}")
                    sockets_list.remove(notified_socket)

if __name__ == "__main__":
    start_server()