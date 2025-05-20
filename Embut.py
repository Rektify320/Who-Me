import os
import webbrowser
import datetime
import openai
import pyttsx3
import yt_dlp
import vlc
import speech_recognition as sr

openai.api_key = "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"

# Inisialisasi suara
engine = pyttsx3.init()
engine.setProperty('rate', 160)

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
        print("chrome terbuka")
    elif name == "Notepad":
        os.system("start Notepad")
        print("Notepad terbuka")
    else:
        print("unknown aplication")

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
        ngomong("ini jawabannya...")
        print(jawaban)
        ngomong(jawaban[:100])
    except Exception as e:
        print(f"⚠️ Gagal ambil jawaban dari Embut: {e}")

def play_lagu(judul):
    global player 
    try:
        # Set path VLC
        vlc_path = r"C:\Program Files\VideoLAN\VLC\vlc.exe"
        os.environ["PATH"] += os.pathsep + os.path.dirname(vlc_path)

        # Konfigurasi yt-dlp buat search dan ambil audio
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'default_search': 'ytsearch1',  # cari dan ambil 1 hasil
            'nocheckcertificate': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(judul, download=False)
            stream_url = info['entries'][0]['url']

        # Putar audio via VLC
        ngomong(f"Muterin lagu {judul} langsung dari YouTube...")
        instance = vlc.Instance()
        player = instance.media_player_new()
        media = instance.media_new(stream_url)
        player.set_media(media)
        player.play()

    except Exception as e:
        ngomong(f"Gagal muter lagu: {e}")

def pause_lagu():
    global player
    if player is not None:
        player.pause()
        ngomong("Lagu dijeda")
    else:
        ngomong("Tidak ada lagu yang sedang dijeda")

def stop_lagu():
    global player
    if player is not None:
        player.stop()
        ngomong("Lagu dihentikan")
        player = None
    else:
        ngomong("Tidak ada lagu yang sedang dihentikan")

def tampilkan_menu():
    print("""
=====================📜 MENU EMBUT =====================

🎵 MUSIK:
  play [judul lagu]     ➜ Muterin lagu langsung dari YouTube
  pause                 ➜ Jeda lagu yang sedang dijeda
  stop                  ➜ Hentikan lagu yang sedang dihentikan

🌐 APLIKASI:
  buka chrome           ➜ Buka Google Chrome
  buka Notepad          ➜ Buka Notepad/Notepad++

🤖 AI CODING:
  tanya [perintah]      ➜ Nanya soal coding ke GPT

🗣️ INPUT MODE:
  suara                 ➜ Perintah pakai suara
  ketik                 ➜ Perintah pakai ketikan

🔧 LAINNYA:
  menu                  ➜ Lihat menu ini lagi
  clear                 ➜ Hapus semua perintah yang diinput
  exit                  ➜ Keluar dari Embut 
=======================================================
""")

def proses_perintah(perintah):
    if perintah.startswith("buka "):
        app = perintah.replace("buka ", "")
        buka_aplikasi(app)
    elif perintah.startswith("tanya "):
        prompt = perintah.replace("tanya ", "")
        bantu_ngoding(prompt)
    elif perintah.startswith("play "):
        judul = perintah.replace("play ", "")
        play_lagu(judul)
    elif perintah == "pause":
        pause_lagu()
    elif perintah == "stop":
        stop_lagu()
    elif perintah == "menu":
        tampilkan_menu()
    elif perintah == "clear":
        os.system('cls' if os.name == 'nt' else 'clear')
    elif perintah == "exit":
        ngomong("Sampai jumpa Putra!")
        exit()
    else:
        ngomong("Perintah tidak dikenali.")

def main():
    ngomong("Halo, gue Embut. Mau ketik atau ngomong?")
    tampilkan_menu()
    while True:
        mode = input("Ketik [suara] atau [ketik]: ").lower()
        if mode == "suara":
            command = hear_the_sound()
        else:
            waktu = datetime.datetime.now().strftime("%H:%M")
            prompt = f"\033[92m[{waktu}] > \033[0m"
            command = input(prompt).lower()

        if command:
            proses_perintah(command)


if __name__ == "__main__":
    main()
