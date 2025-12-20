import time
from database import DuplicateIDError

def is_file_expired(expire_at):
    if expire_at == 0:
        return False
    current_time = int(time.time())
    return current_time >= expire_at

def separate_extension(filename):
    if '.' not in filename:
        raise ValueError("Filename does not contain an extension.")
    name, ext = filename.rsplit('.', 1)
    return name, ext

def get_expire_time(expire_seconds):
    if expire_seconds <= 0:
        return 0
    return int(time.time()) + expire_seconds