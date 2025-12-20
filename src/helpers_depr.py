import time

class FileSaveError(Exception):
    pass

def separate_extension(filename):
    if '.' not in filename:
        raise ValueError("Filename does not contain an extension.")
    name, ext = filename.rsplit('.', 1)
    return name, ext

def save(file, filename):
    filepath = f"./uploads/{filename}"
    file.save(filepath)
    return filepath

def get_expire_time(expire_seconds):
    if expire_seconds <= 0:
        return 0
    return int(time.time()) + expire_seconds