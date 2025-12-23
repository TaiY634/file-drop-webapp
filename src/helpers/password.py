import bcrypt

def hash_password(pw: str) -> bytes:
  salt = bcrypt.gensalt(rounds=12)
  return bcrypt.hashpw(pw.encode(), salt).decode()

def verify_password(password: str, stored_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), stored_hash.encode())