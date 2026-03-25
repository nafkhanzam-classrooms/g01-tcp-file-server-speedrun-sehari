import socket
import select
import os
import sys

# Pengecekan OS (karena hanya bisa untuk linux)
if not hasattr(select, 'poll'):
    print("Error: OS ini (Windows) tidak mendukung select.poll(). Gunakan Linux/Mac/WSL.")
    sys.exit()

HOST = '127.0.0.1'
PORT = 5000
BUFFER_SIZE = 4096
SERVER_FOLDER = 'server_files'

if not os.path.exists(SERVER_FOLDER):
    os.makedirs(SERVER_FOLDER)

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    
    poller = select.poll()
    poller.register(server, select.POLLIN)
    
    fd_to_socket = {server.fileno(): server}
    print(f"[LISTENING] Server-Poll berjalan di {HOST}:{PORT}")
    
    while True:
        events = poller.poll()
        for fd, flag in events:
            sock = fd_to_socket[fd]
            
            if flag & select.POLLIN:
                if sock == server:
                    conn, addr = server.accept()
                    print(f"[CONNECTED] {addr} terhubung.")
                    poller.register(conn, select.POLLIN)
                    fd_to_socket[conn.fileno()] = conn
                else:
                    try:
                        data = sock.recv(BUFFER_SIZE).decode('utf-8')
                        if not data:
                            print(f"[DISCONNECTED] Klien terputus.")
                            poller.unregister(sock)
                            del fd_to_socket[fd]
                            continue
                            
                        if data.startswith('CHAT|'):
                            msg = data.split('|', 1)[1]
                            # Broadcast ke fd lain
                            for c_fd, c_sock in fd_to_socket.items():
                                if c_sock != server and c_sock != sock:
                                    c_sock.sendall(f"CHAT|Klien berkata: {msg}".encode('utf-8'))
                        
                        elif data.startswith('LIST|'):
                            files = os.listdir(SERVER_FOLDER)
                            file_list = ", ".join(files) if files else "Kosong"
                            sock.sendall(f"CHAT|File di server: {file_list}".encode('utf-8'))
                            
                        # Logika upload dan download sama seperti server-select
                        elif data.startswith('UPLOAD|'):
                            parts = data.split('|')
                            filename, filesize = parts[1], int(parts[2])
                            filepath = os.path.join(SERVER_FOLDER, filename)
                            bytes_received = 0
                            with open(filepath, 'wb') as f:
                                while bytes_received < filesize:
                                    chunk = sock.recv(min(BUFFER_SIZE, filesize - bytes_received))
                                    if not chunk: break
                                    f.write(chunk)
                                    bytes_received += len(chunk)
                                    
                        elif data.startswith('DOWNLOAD|'):
                            filename = data.split('|')[1]
                            filepath = os.path.join(SERVER_FOLDER, filename)
                            if os.path.exists(filepath):
                                filesize = os.path.getsize(filepath)
                                sock.sendall(f"FILE|{filename}|{filesize}".encode('utf-8'))
                                with open(filepath, 'rb') as f:
                                    while (chunk := f.read(BUFFER_SIZE)):
                                        sock.sendall(chunk)
                            else:
                                sock.sendall(f"CHAT|Error: File tidak ditemukan.".encode('utf-8'))
                    except Exception as e:
                        poller.unregister(sock)
                        del fd_to_socket[fd]
                        
if __name__ == "__main__":
    start_server()