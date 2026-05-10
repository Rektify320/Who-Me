import json
from datetime import datetime

class Logger:
    LEVELS = {'DEBUG': 10, 'INFO': 20, 'WARNING': 30, 'ERROR': 40, 'CRITICAL': 50}

    def __init__(self, level='INFO', log_file=None):
        self.level = self.LEVELS.get(level.upper(), 20)
        self.log_file = log_file
        if self.log_file:
            # buat file jika belum ada
            with open(self.log_file, 'a') as f:
                pass

    def _log(self, level, message, module=''):
        entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': level,
            'module': module,
            'message': message
        }
        # Output ke konsol
        print(f"[{entry['timestamp']}] [{level:7s}] [{module:12s}] {message}")
        # Simpan ke file JSON jika diset
        if self.log_file:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(entry) + '\n')

    def debug(self, msg, module=''):
        if self.level <= 10: self._log('DEBUG', msg, module)

    def info(self, msg, module=''):
        if self.level <= 20: self._log('INFO', msg, module)

    def warning(self, msg, module=''):
        if self.level <= 30: self._log('WARNING', msg, module)

    def error(self, msg, module=''):
        if self.level <= 40: self._log('ERROR', msg, module)

    def critical(self, msg, module=''):
        if self.level <= 50: self._log('CRITICAL', msg, module)