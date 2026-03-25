import socket
import os

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
    print(f"[LISTENING] Server-Sync berjalan di {HOST}:{PORT}")
    
    while True:
        print("[WAITING] Menunggu 1 klien untuk terhubung...")
        conn, addr = server.accept()
        print(f"[CONNECTED] {addr} terhubung. Klien lain harus mengantre.")
        
        try:
            while True:
                data = conn.recv(BUFFER_SIZE).decode('utf-8')
                if not data: break
                
                if data.startswith('CHAT|'):
                    msg = data.split('|', 1)[1]
                    print(f"[{addr}] Chat: {msg}")
                    # Hanya ada 1 klien, tidak ada yang bisa di-broadcast
                    # Kita echo kembali ke klien yang sama sebagai konfirmasi
                    conn.sendall(f"CHAT|Server Echo: {msg}".encode('utf-8'))
                    
                elif data.startswith('LIST|'):
                    files = os.listdir(SERVER_FOLDER)
                    file_list = ", ".join(files) if files else "Kosong"
                    conn.sendall(f"CHAT|File di server: {file_list}".encode('utf-8'))
                    
                elif data.startswith('UPLOAD|'):
                    parts = data.split('|')
                    filename = parts[1]
                    filesize = int(parts[2])
                    
                    filepath = os.path.join(SERVER_FOLDER, filename)
                    bytes_received = 0
                    with open(filepath, 'wb') as f:
                        while bytes_received < filesize:
                            chunk = conn.recv(min(BUFFER_SIZE, filesize - bytes_received))
                            if not chunk: break
                            f.write(chunk)
                            bytes_received += len(chunk)
                    print(f"[UPLOAD] {filename} diterima.")
                    conn.sendall(f"CHAT|Upload {filename} sukses.".encode('utf-8'))
                    
                elif data.startswith('DOWNLOAD|'):
                    filename = data.split('|')[1]
                    filepath = os.path.join(SERVER_FOLDER, filename)
                    if os.path.exists(filepath):
                        filesize = os.path.getsize(filepath)
                        conn.sendall(f"FILE|{filename}|{filesize}".encode('utf-8'))
                        with open(filepath, 'rb') as f:
                            while (chunk := f.read(BUFFER_SIZE)):
                                conn.sendall(chunk)
                        print(f"[DOWNLOAD] {filename} dikirim.")
                    else:
                        conn.sendall(f"CHAT|Error: File tidak ditemukan.".encode('utf-8'))
        except Exception as e:
            print(f"[ERROR] {e}")
        finally:
            conn.close()
            print(f"[DISCONNECTED] {addr} keluar.\n")

if __name__ == "__main__":
    start_server()