<img width="678" height="437" alt="Screenshot (1098)" src="https://github.com/user-attachments/assets/5317056e-e9b1-47b4-bda4-540829744724" />

```
# 🌀 VortexSnare
CLI-Based SSH & FTP Honeypot – The Ultimate Deception Protocol
VortexSnare adalah honeypot berbasis command-line yang dirancang untuk menjebak, mencatat, dan menganalisis serangan brute-force pada layanan SSH dan FTP. Tool ini cocok untuk pembelajaran keamanan jaringan, simulasi serangan, dan pengumpulan threat intelligence secara aman.

---

## 🚀 Fitur

- 🔐 SSH Honeypot (Fake OpenSSH Banner)
- 📁 FTP Honeypot (USER/PASS Interception)
- 📊 Real-time attack monitoring
- 🧠 Statistik serangan otomatis
- 🗂 Logging forensik (JSON & CSV)
- 🎨 Output terminal berwarna (ANSI)
- 🖥 Cross-platform (Windows, Linux, macOS)
- ⚙️ Pure Python (tanpa dependency eksternal)

---

## 🛠 Arsitektur Singkat

```

Attacker
├── SSH Brute Force ──▶ SSH Honeypot
└── FTP Brute Force ──▶ FTP Honeypot
│
▼
Intelligence Logs
(JSON & CSV Files)

````

---

## 📦 Persyaratan

- Python 3.8 atau lebih baru
- Hak akses membuka port (disarankan non-root)

---

## 📥 Instalasi

```bash
https://github.com/hashizumee/VortexSnare.git
cd vortexsnare
````

---

## ▶️ Menjalankan VortexSnare

### Default Port

```bash
python vortexsnare.py
```

* SSH : 2222
* FTP : 2121

### Custom Port

```bash
python vortexsnare.py --ssh-port 2223 --ftp-port 2122
```

---

## 🧪 Pengujian Serangan

### SSH Test

```bash
ssh root@127.0.0.1 -p 2222
```

### FTP Test

```bash
ftp 127.0.0.1 2121
```

Masukkan username dan password bebas. Semua percobaan akan dicatat sebagai serangan.

---

## 📂 Struktur Log

```
intelligence_logs/
├── vortex_intel_YYYYMMDD_HHMMSS.json
└── vortex_intel_YYYYMMDD_HHMMSS.csv
```

### Contoh Format JSON

```json
{
  "timestamp": "2026-01-21T10:15:22",
  "protocol": "SSH",
  "source_ip": "192.168.1.10",
  "source_port": 53422,
  "username": "root",
  "password": "toor",
  "success": false,
  "additional_info": "Brute-force"
}
```

---

## 📊 Statistik Otomatis

Saat program dihentikan (CTRL + C), VortexSnare akan menampilkan:

* Durasi sesi
* Jumlah IP penyerang unik
* Total serangan SSH & FTP
* Top 5 IP penyerang
* Lokasi file log forensik

---

## ⚠️ Disclaimer

Tool ini dibuat **hanya untuk tujuan edukasi, riset, dan defensive security**.

❌ Dilarang digunakan untuk:

* Aktivitas ilegal
* Menjebak pengguna tanpa izin
* Lingkungan produksi tanpa sandbox

✅ Disarankan:

* Gunakan VM atau lab testing
* Aktifkan firewall & monitoring tambahan



