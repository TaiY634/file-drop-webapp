import time

def is_file_expired(expire_at):
    if expire_at == -1:
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

def calculate_token_increment(last_refill_time, increment_interval) -> tuple[int, int]:
    current_time = int(time.time())
    elapsed = current_time - last_refill_time
    increments = elapsed // increment_interval
    new_refill_time = last_refill_time + increments * increment_interval
    return increments, new_refill_time