import bcrypt

def hash_password(pw: str) -> bytes:
  salt = bcrypt.gensalt(rounds=12)
  return bcrypt.hashpw(pw.encode(), salt)

def verify_password(password: str, stored_hash: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), stored_hash)