import os, json, hashlib, time, sys, requests, socket
from getpass import getpass

class AuthSystem:
    DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'users.json')
    IP_LOCK_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'ip_lock.json')
    DEFAULT_ADMIN = 'admin'
    DEFAULT_PASS = 'admin'
    DEFAULT_TOKENS_USER = 10
    UNLIMITED_TOKENS = 99999
    MAX_ATTEMPTS_PER_IP = 10          # batas total percobaan gagal per IP
    IP_LOCK_DURATION = 300            # lama kunci dalam detik (5 menit)

    def __init__(self):
        os.makedirs(os.path.dirname(self.DB_PATH), exist_ok=True)
        self.users = self._load_db()
        self.ip_lock_data = self._load_ip_lock()
        # Migrasi database lama jika masih format hash saja
        if self.DEFAULT_ADMIN in self.users and not isinstance(self.users[self.DEFAULT_ADMIN], dict):
            self._migrate_db()
        # Hapus kunci IP yang sudah kadaluwarsa saat startup
        self._clean_ip_locks()

    # ==================== IP LOCK METHODS ====================
    def _load_ip_lock(self) -> dict:
        if not os.path.exists(self.IP_LOCK_PATH):
            return {}
        with open(self.IP_LOCK_PATH, 'r') as f:
            return json.load(f)

    def _save_ip_lock(self):
        with open(self.IP_LOCK_PATH, 'w') as f:
            json.dump(self.ip_lock_data, f, indent=2)

    def _clean_ip_locks(self):
        now = time.time()
        expired = [ip for ip, data in self.ip_lock_data.items()
                   if data.get('lock_until', 0) < now]
        for ip in expired:
            del self.ip_lock_data[ip]
        if expired:
            self._save_ip_lock()

    @staticmethod
    def get_client_ip() -> str:
        """Ambil IP client (via SSH_CLIENT atau fallback)."""
        ssh_client = os.environ.get('SSH_CLIENT', '')
        if ssh_client:
            return ssh_client.split()[0]
        # Jika tidak ada, coba socket (untuk koneksi lokal)
        try:
            # Ambil IP dari koneksi socket (kurang akurat jika multi-interface)
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return '127.0.0.1'

    def is_ip_locked(self, ip: str):
        """Return (is_locked, remaining_seconds)."""
        self._clean_ip_locks()
        lock_until = self.ip_lock_data.get(ip, {}).get('lock_until', 0)
        if time.time() < lock_until:
            return True, int(lock_until - time.time())
        return False, 0

    def record_failed_attempt(self, ip: str):
        """Catat percobaan gagal, return True jika IP baru saja dikunci."""
        if ip not in self.ip_lock_data:
            self.ip_lock_data[ip] = {'attempts': 0, 'lock_until': 0}
        self.ip_lock_data[ip]['attempts'] += 1
        if self.ip_lock_data[ip]['attempts'] >= self.MAX_ATTEMPTS_PER_IP:
            self.ip_lock_data[ip]['lock_until'] = time.time() + self.IP_LOCK_DURATION
            self._save_ip_lock()
            return True
        self._save_ip_lock()
        return False

    def reset_ip_attempts(self, ip: str):
        """Hapus data IP setelah login sukses."""
        if ip in self.ip_lock_data:
            del self.ip_lock_data[ip]
            self._save_ip_lock()

    # ==================== USER DATABASE ====================
    def _migrate_db(self):
        new_users = {}
        for user, pass_hash in self.users.items():
            if user == self.DEFAULT_ADMIN:
                new_users[user] = {
                    'password': pass_hash,
                    'role': 'owner',
                    'tokens': self.UNLIMITED_TOKENS
                }
            else:
                new_users[user] = {
                    'password': pass_hash,
                    'role': 'user',
                    'tokens': self.DEFAULT_TOKENS_USER
                }
        self.users = new_users
        self._save_db()

    def _load_db(self) -> dict:
        if not os.path.exists(self.DB_PATH):
            default = {
                self.DEFAULT_ADMIN: {
                    'password': self._hash_password(self.DEFAULT_PASS),
                    'role': 'owner',
                    'tokens': self.UNLIMITED_TOKENS
                }
            }
            with open(self.DB_PATH, 'w') as f:
                json.dump(default, f, indent=2)
            return default
        with open(self.DB_PATH, 'r') as f:
            return json.load(f)

    def _save_db(self):
        with open(self.DB_PATH, 'w') as f:
            json.dump(self.users, f, indent=2)

    @staticmethod
    def _hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self, username: str, password: str) -> bool:
        user = self.users.get(username)
        if not user:
            return False
        return user['password'] == self._hash_password(password)

    def get_role(self, username: str) -> str:
        return self.users.get(username, {}).get('role', 'user')

    def is_admin(self, username: str) -> bool:
        return self.get_role(username) == 'owner'

    def get_tokens(self, username: str) -> int:
        return self.users.get(username, {}).get('tokens', 0)

    def deduct_token(self, username: str) -> bool:
        if self.is_admin(username):
            return True
        user = self.users.get(username)
        if not user or user['tokens'] <= 0:
            return False
        user['tokens'] -= 1
        self._save_db()
        return True

    def add_user(self, username: str, password: str, tokens: int = None):
        if username in self.users:
            return False, "User already exists."
        self.users[username] = {
            'password': self._hash_password(password),
            'role': 'user',
            'tokens': tokens if tokens is not None else self.DEFAULT_TOKENS_USER
        }
        self._save_db()
        return True, "User added successfully."

    def delete_user(self, username: str):
        if username not in self.users:
            return False, "User not found."
        if username == self.DEFAULT_ADMIN:
            return False, "Cannot delete main owner."
        del self.users[username]
        self._save_db()
        return True, "User deleted."

    def set_tokens(self, username: str, tokens: int):
        if username not in self.users:
            return False, "User not found."
        self.users[username]['tokens'] = tokens
        self._save_db()
        return True, f"Tokens updated to {tokens}."

    def list_users(self):
        result = []
        for user, data in self.users.items():
            result.append({
                'username': user,
                'role': data['role'],
                'tokens': data['tokens']
            })
        return result

    # ==================== UI & CONNECTIVITY ====================
    @staticmethod
    def rainbow_text(text, shift=0):
        colors = [31, 33, 32, 36, 34, 35]
        result = ''
        for i, ch in enumerate(text):
            color = colors[(i + shift) % len(colors)]
            result += f'\033[{color}m{ch}\033[0m'
        return result

    @staticmethod
    def colorize(text, color_code):
        return f'\033[{color_code}m{text}\033[0m'

    def check_connectivity(self):
        """Cek koneksi internet secara nyata."""
        print(f"\n[*] Checking connectivity...")
        try:
            r = requests.get("https://google.com", timeout=5)
            if r.status_code == 200:
                print("    " + self.colorize("[OK] Internet connection detected", 32))
                return True
        except:
            pass
        print("    " + self.colorize("[WARN] No internet connection – offline mode", 33))
        return False

    def show_hacker_loading(self, message="Initializing toolkit"):
        self.check_connectivity()
        stages = [
            '[■□□□□□□□□□] 10% loading engine',
            '[■■□□□□□□□□] 25% loading modules',
            '[■■■□□□□□□□] 38% loading signatures',
            '[■■■■■□□□□□] 54% establishing handlers',
            '[■■■■■■■□□□] 72% finalizing',
            '[■■■■■■■■■□] 89% almost ready',
            '[■■■■■■■■■■] 100% ready'
        ]
        print(f"\n[*] {message}...")
        for idx, stage in enumerate(stages):
            colored_stage = self.rainbow_text(stage, shift=idx)
            sys.stdout.write(f'\r    {colored_stage}')
            sys.stdout.flush()
            time.sleep(0.25)
        ok_text = self.rainbow_text(' [OK]', shift=len(stages))
        print(ok_text)
        time.sleep(0.2)