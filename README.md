[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/mRmkZGKe)
# Network Programming - Assignment G01

## Anggota Kelompok
| Nama           | NRP        | Kelas     |
| ---            | ---        | ----------|
| Erica Triana Widyastuti |5025241069|Pemrograman Jaringan-D|
| Fayza Lathifah Humam         |5025241094|Pemrograman Jaringan-D|

## Link Youtube (Unlisted)
Link ditaruh di bawah ini
```

```

## Penjelasan Program
Program ini mengimplementasikan konsep multi-client TCP file server dengan empat pendekatan concurrency berbeda, beserta satu file client universal. Keempat server memiliki fitur yang sama yaitu broadcast chat, list file, upload, dan download, namun berbeda dalam cara tiap server menangani banyak klien secara bersamaan. Berikut adalah penjelasan tiap file:

### 1. server-sync.py
`server_sync.py` adalah implementasi blocking server yang hanya dapat melayani satu klien dalam satu waktu. Server yang di-`accept()` hanya bisa lanjut ke klien berikutnya setelah klien saat ini sudah disconnect. Struktur utama server ini adalah dua nested loop:

```python
while True:                     
    conn, addr = server.accept()     # block sampai ada klien
    
    while True:                      # melayani klien ini
        data = conn.recv(BUFFER_SIZE)
        if not data: break
        ...
    
    conn.close()                     # baru setelah ini, terima next klien
```

Selama loop dalam berjalan melayani Client 1, server tidak bisa menerima Client 2. Client 2 hanya bisa masuk ke *backlog* TCP (karena `server.listen(5)`), dan baru mendapat giliran setelah Client 1 disconnect.

### 2. server-select.py

### 3. server-poll.py

### 4. server-thread.py

### 5. client.py
`client.py` adalah terminal client yang dapat bekerja dengan keempat variasi server yang sudah dibahas sebelumnya dengan memisahkan dua tanggung jawab ke dalam dua thread berbeda. Satu thread untuk menerima pesan dari server (berjalan di background), dan satu thread utama untuk membaca input dari user. Seperti berikut:

```python
# Thread background untuk menerima pesan
threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

# Thread utama untuk mengirim input user
while True:
    msg = input("")
    ...
```

Thread penerima dibuat sebagai daemon thread (`daemon=True`) yang akan otomatis mati ketika program utama selesai. Semua komunikasi antara client dan server menggunakan delimiter-based framing dengan karakter `|` sebagai pemisah (sesuai Method 4: Delimiter dari materi PPT). Format pesannya adalah sebagai berikut:

| Pesan | Format |
|---|---|
| Chat biasa | `CHAT\|isi pesan` |
| Notifikasi file masuk | `FILE\|namafile\|ukuran_bytes` |
| Minta daftar file | `LIST\|` |
| Upload file | `UPLOAD\|namafile\|ukuran_bytes` |
| Download file | `DOWNLOAD\|namafile` |

Untuk transfer file, client mengirim header terlebih dahulu (`UPLOAD|nama|ukuran`), lalu langsung mengirim byte file tersebut setelahnya. Di sisi penerima, ukuran file dari header digunakan untuk menentukan berapa byte yang harus dibaca, melalui kombinasi antara delimiter (untuk header) dan length-prefix (untuk body file).

## Screenshot Hasil
