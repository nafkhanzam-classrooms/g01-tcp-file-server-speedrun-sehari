import socketserver
import os

HOST = '127.0.0.1'
PORT = 5000
BUFFER_SIZE = 4096
SERVER_FOLDER = 'server_files'

# Buat folder server jika belum ada
if not os.path.exists(SERVER_FOLDER):
    os.makedirs(SERVER_FOLDER)

# Set untuk menyimpan semua klien yang terhubung (untuk keperluan broadcast)
clients = set()

class ChatAndFileHandler(socketserver.BaseRequestHandler):
    
    def setup(self):
        """Fungsi ini dipanggil otomatis saat klien baru terhubung."""
        print(f"[CONNECTED] {self.client_address} terhubung.")
        clients.add(self.request) # self.request adalah socket milik klien

    def handle(self):
        """Fungsi utama untuk menangani komunikasi dengan klien."""
        while True:
            try:
                # Terima data awal (header/pesan)
                data = self.request.recv(BUFFER_SIZE).decode('utf-8')
                if not data:
                    break
                
                # --- FITUR CHAT / BROADCAST ---
                if data.startswith('CHAT|'):
                    msg = data.split('|', 1)[1]
                    print(f"[{self.client_address}] Chat: {msg}")
                    self.broadcast(f"CHAT|[{self.client_address}] berkata: {msg}")
                    
                # --- FITUR LIST FILE ---
                elif data.startswith('LIST|'):
                    files = os.listdir(SERVER_FOLDER)
                    file_list = ", ".join(files) if files else "Folder kosong"
                    self.request.sendall(f"CHAT|File di server: {file_list}".encode('utf-8'))
                    
                # --- FITUR UPLOAD ---
                elif data.startswith('UPLOAD|'):
                    parts = data.split('|')
                    filename = parts[1]
                    filesize = int(parts[2])
                    filepath = os.path.join(SERVER_FOLDER, filename)
                    
                    bytes_received = 0
                    with open(filepath, 'wb') as f:
                        while bytes_received < filesize:
                            chunk = self.request.recv(min(BUFFER_SIZE, filesize - bytes_received))
                            if not chunk: break
                            f.write(chunk)
                            bytes_received += len(chunk)
                    
                    print(f"[UPLOAD] {filename} berhasil diupload oleh {self.client_address}")
                    self.broadcast(f"CHAT|{self.client_address} baru saja mengupload file '{filename}'")
                    
                # --- FITUR DOWNLOAD ---
                elif data.startswith('DOWNLOAD|'):
                    filename = data.split('|')[1]
                    filepath = os.path.join(SERVER_FOLDER, filename)
                    
                    if os.path.exists(filepath):
                        filesize = os.path.getsize(filepath)
                        # Kirim header FILE ke klien
                        self.request.sendall(f"FILE|{filename}|{filesize}".encode('utf-8'))
                        
                        # Kirim isi file
                        with open(filepath, 'rb') as f:
                            while (chunk := f.read(BUFFER_SIZE)):
                                self.request.sendall(chunk)
                        print(f"[DOWNLOAD] {filename} dikirim ke {self.client_address}")
                    else:
                        self.request.sendall(f"CHAT|Error: File '{filename}' tidak ditemukan di server.".encode('utf-8'))

            except Exception as e:
                print(f"[ERROR] {self.client_address}: {e}")
                break

    def finish(self):
        """Fungsi ini dipanggil otomatis saat klien terputus."""
        print(f"[DISCONNECTED] {self.client_address} terputus.")
        clients.remove(self.request)

    def broadcast(self, message):
        """Fungsi bantuan untuk mengirim pesan ke semua klien kecuali pengirim."""
        for client in list(clients):
            if client != self.request:
                try:
                    client.sendall(message.encode('utf-8'))
                except:
                    pass

# Membuat class Server Multi-Thread
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True        # Agar thread klien otomatis mati jika server dimatikan
    allow_reuse_address = True   # Agar port bisa langsung dipakai ulang jika server direstart

if __name__ == "__main__":
    print(f"[LISTENING] Server-Thread (menggunakan socketserver) berjalan di {HOST}:{PORT}")
    # Menjalankan server
    with ThreadedTCPServer((HOST, PORT), ChatAndFileHandler) as server:
        server.serve_forever()