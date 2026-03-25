import socket
import threading
import os
import sys

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5000
BUFFER_SIZE = 4096
CLIENT_FOLDER = 'client_files'

# Buat folder jika belum ada
if not os.path.exists(CLIENT_FOLDER):
    os.makedirs(CLIENT_FOLDER)

def receive_messages(sock):
    while True:
        try:
            # Terima header/pesan
            data = sock.recv(BUFFER_SIZE).decode('utf-8')
            if not data:
                break
            
            if data.startswith('CHAT|'):
                print(f"\n[Server/Broadcast] {data.split('|', 1)[1]}")
            
            elif data.startswith('FILE|'):
                # Format: FILE|namafile|ukuran
                parts = data.split('|')
                filename = parts[1]
                filesize = int(parts[2])
                
                print(f"\n[Menerima file {filename} ({filesize} bytes)...]")
                filepath = os.path.join(CLIENT_FOLDER, filename)
                
                bytes_received = 0
                with open(filepath, 'wb') as f:
                    while bytes_received < filesize:
                        chunk = sock.recv(min(BUFFER_SIZE, filesize - bytes_received))
                        if not chunk: break
                        f.write(chunk)
                        bytes_received += len(chunk)
                print(f"\n[Download selesai: {filename}]")
                
        except Exception as e:
            print(f"\n[Terputus dari server: {e}]")
            sock.close()
            break

def start_client():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_HOST, SERVER_PORT))
    print("[Terhubung ke Server. Ketik pesan atau gunakan perintah: /list, /upload <file>, /download <file>]")

    # Jalankan thread untuk menerima pesan
    threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

    while True:
        msg = input("")
        if msg.lower() == '/quit':
            sock.close()
            sys.exit()
            
        elif msg.startswith('/list'):
            sock.sendall('LIST|'.encode('utf-8'))
            
        elif msg.startswith('/upload '):
            filename = msg.split(' ')[1]
            filepath = os.path.join(CLIENT_FOLDER, filename)
            if os.path.exists(filepath):
                filesize = os.path.getsize(filepath)
                # Kirim header
                sock.sendall(f"UPLOAD|{filename}|{filesize}".encode('utf-8'))
                
                # Kirim file
                with open(filepath, 'rb') as f:
                    while (chunk := f.read(BUFFER_SIZE)):
                        sock.sendall(chunk)
                print(f"[Upload {filename} dikirim]")
            else:
                print("[Error: File tidak ditemukan di folder klien]")
                
        elif msg.startswith('/download '):
            filename = msg.split(' ')[1]
            sock.sendall(f"DOWNLOAD|{filename}".encode('utf-8'))
            
        else:
            # Kirim sebagai chat biasa
            sock.sendall(f"CHAT|{msg}".encode('utf-8'))

if __name__ == "__main__":
    start_client()