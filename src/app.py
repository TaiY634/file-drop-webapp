import uuid
from flask import Flask, render_template, request, session, send_file 
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

from helpers.file_helpers import is_file_expired, separate_extension, get_expire_time
from helpers.password import *
from helpers.custom_exceptions import DuplicateIDError

import database
import filestorage
import argparse

app = Flask(__name__)
app.secret_key = os.urandom(24)
limiter = Limiter(app=app, key_func=get_remote_address, default_limits=[])
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'webp', 'gif', 'zip', 'rar'])
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


parser = argparse.ArgumentParser()
parser.add_argument('--no-use-local', action='store_true', help="Use AWS S3/DynamoDB instead of local storage")
args = parser.parse_args()

app.config['USE_LOCAL'] = not args.no_use_local  # Set to False to use S3 and DynamoDB

@app.route("/")
def index():
    print('using local storage:', app.config['USE_LOCAL'])
    return render_template("index.html")

@app.route("/download/<file_id>", methods=["GET", "POST"])
@limiter.limit("20 per minute")
def download(file_id):
    db = database.get_database(local=app.config['USE_LOCAL'])
    storage = filestorage.get_filestorage(local=app.config['USE_LOCAL'])
    file_metadata = db.get(file_id)
    if not file_metadata or is_file_expired(file_metadata['expire_at']):
        return render_template("error.html", error="File has expired or does not exist."), 404


        
    error = None
    has_password = file_metadata['password_hash'] is not None
    authenticated = session.get(f'authenticated_{file_metadata["file_id"]}', not has_password)

    filename = file_metadata['filename']
    key = file_metadata['key']
    # print("filename:", filename)
    # print("Has password:", has_password)
    # print('Stored hash type:', type(file_metadata['password_hash']))
    # print('Stored hash value:', file_metadata['password_hash'])
    # print("Authenticated:", authenticated)

    # If password-protected, verify
    if has_password:
        if request.method == "POST":
            if authenticated:
                return storage.download(key, filename=filename)
            password = request.form.get("password", "")
            stored_hash = file_metadata['password_hash']
            if not stored_hash or not verify_password(password, stored_hash):
                error = "Incorrect password."
            else:
                # Password correct, send file
                session[f'authenticated_{file_metadata["file_id"]}'] = True
                return render_template("download.html", filename=filename, error=None, has_password=has_password, authenticated=True)
    
        return render_template("download.html", filename=filename, error=error, has_password=has_password, authenticated=authenticated)
    # If not password-protected, show confirmation form
    else:
        if request.method == "POST":
            return storage.download(key, filename=filename)
        else:
            return render_template("download.html", filename=filename, has_password=has_password, authenticated=authenticated)



@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        uploaded_file = request.files.get("file")
        if not uploaded_file or uploaded_file.filename == '':
            return render_template("error.html", error="No file provided or filename is empty."), 400
        
        filename = uploaded_file.filename
        _, ext = separate_extension(filename)

        if ext not in app.config['ALLOWED_EXTENSIONS']:
            return render_template("error.html", error=f"File type {ext} not allowed."), 400
        
        expires_in = request.form.get("expiresIn", type=int, default=0)
        expire_time = get_expire_time(expires_in)
        password = request.form.get("password", default="")
        hash = hash_password(password) if password else None
        file_id = uuid.uuid4().hex
        key = f"{file_id}_{filename}"
        
        db = database.get_database(local=app.config['USE_LOCAL'])
        storage = filestorage.get_filestorage(local=app.config['USE_LOCAL'])

        while True:
            try:
                db.create(file_id, filename, key, expire_time, downloads=0, attempts=0, password_hash=hash)
                break
            except DuplicateIDError:
                print("Duplicate file_id generated, retrying...")
                file_id = uuid.uuid4().hex
                key = f"{file_id}_{filename}"

        storage.save(uploaded_file, key)
            
        download_link = request.url_root + "download/" + file_id
        return render_template("upload_success.html", filename=filename, download_link=download_link)
    return render_template("upload.html")

# @app.route("/drop", methods=["GET", "POST"])
# def drop():
#     if request.method == "POST":
#         sql.drop_files()
#         return "File table dropped."
#     return '''
#     <form method="POST">
#         <button type="submit">Drop Files</button>
#     </form>
#     '''

@app.route("/admin")
def admin():
    db = database.get_database(local=app.config['USE_LOCAL'])
    metadatas = db._get_all_data()
    return render_template("admin.html", metadatas=metadatas)

# @app.route("/update_deleted_status")
# def update_deleted_status():
#     sql.update_all_deleted_status()
#     return "" \
#     "<body>Deleted status updated. <br><a href='/admin'>Back to Admin</a></body>"

if __name__ == "__main__":
    app.run(debug=True)