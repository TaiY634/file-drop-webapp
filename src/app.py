from flask import Flask, render_template, request, session, send_file 
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

from helpers import *
from password import *
import sql


app = Flask(__name__)
app.secret_key = os.urandom(24)
limiter = Limiter(app=app, key_func=get_remote_address, default_limits=[])
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route("/")
def index():
    sql.create_file_table()
    print(sql.get_all_files())
    return render_template("index.html")

@app.route("/download/<filename>", methods=["GET", "POST"])
@limiter.limit("20 per minute")
def download(filename):
    filepath = sql.get_filepath_by_filename(filename)
    if not filepath or sql.is_file_expired(filename):
        return render_template("error.html", error="File has expired or does not exist."), 404


        
    error = None
    has_password = sql.has_password(filename)
    authenticated = session.get(f'authenticated_{filename}', not has_password)
    print("filename:", filename)
    print("Has password:", has_password)
    print("Authenticated:", authenticated)

    # If password-protected, verify
    if has_password:
        if request.method == "POST":
            if authenticated:
                return send_file(filepath, as_attachment=True)
            password = request.form.get("password", "")
            stored_hash = sql.get_password_hash(filename)
            if not stored_hash or not verify_password(password, stored_hash):
                error = "Incorrect password."
            else:
                # Password correct, send file
                session[f'authenticated_{filename}'] = True
                return render_template("download.html", filename=filename, error=None, has_password=has_password, authenticated=True)
    
        return render_template("download.html", filename=filename, error=error, has_password=has_password, authenticated=authenticated)
    # If not password-protected, show confirmation form
    else:
        if request.method == "POST":
            return send_file(filepath, as_attachment=True)
        else:
            return render_template("download.html", filename=filename, has_password=has_password, authenticated=authenticated)

@app.route("/files/<filename>")
def file(filename):
    filepath = sql.get_filepath_by_filename(filename)
    if not filepath:
        return "File not found", 404
    if sql.is_file_expired(filename):
        return "File has expired", 404
    print("Downloading file:", filepath)
    return send_file(filepath, as_attachment=True)


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        uploaded_file = request.files.get("file")
        if not uploaded_file or uploaded_file.filename == '':
            return render_template("error.html", error="No file provided or filename is empty."), 400
        
        name, ext = separate_extension(uploaded_file.filename)
        filename = f'{name}-{int(time.time())}.{ext}'
        filepath = save(uploaded_file, filename)
        expires_in = request.form.get("expiresIn", type=int, default=0)
        expire_time = get_expire_time(expires_in)
        password = request.form.get("password", default="")
        hash = hash_password(password) if password else None
        sql.add_file(filename, filepath, expire_time, hash)
        return render_template("upload_success.html", filename=filename, site_url = request.url_root, filepath=filepath)
    return render_template("upload.html")

@app.route("/drop", methods=["GET", "POST"])
def drop():
    if request.method == "POST":
        sql.drop_files()
        return "File table dropped."
    return '''
    <form method="POST">
        <button type="submit">Drop Files</button>
    </form>
    '''

@app.route("/admin")
def admin():
    files = sql.get_all_files()
    return render_template("admin.html", files=files)

@app.route("/update_deleted_status")
def update_deleted_status():
    sql.update_all_deleted_status()
    return "" \
    "<body>Deleted status updated. <br><a href='/admin'>Back to Admin</a></body>"

if __name__ == "__main__":
    app.run(debug=True)