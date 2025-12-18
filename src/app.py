from flask import Flask, render_template, request, send_from_directory, send_file
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

from helpers import *
from password import *
import sql


app = Flask(__name__)
limiter = Limiter(app=app, key_func=get_remote_address, default_limits=[])
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route("/")
def index():
    sql.create_file_table()
    print(sql.get_all_files())
    return render_template("index.html")

@app.route("/download/<filename>", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def download(filename):
    if request.method == "POST":
        password = request.form.get("password", "")
        stored_hash = sql.get_password_hash(filename)
        if not stored_hash or not verify_password(password, stored_hash):
            return render_template("password.html", filename=filename, error="Incorrect password.")
        return render_template("download.html", filename=filename)
    
    if sql.is_file_expired(filename):
        return render_template("error.html", error ="File has expired or does not exist."), 404
    if sql.has_password(filename):
        return render_template("password.html", filename=filename)
    
    return render_template("download.html", filename=filename)

@app.route("/files/<filename>")
def file(filename):
    filepath = sql.get_filepath_by_filename(filename)
    if not filepath:
        return "File not found", 404
    print("Downloading file:", filepath)
    return send_file(filepath, as_attachment=True)


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        uploaded_file = request.files.get("file")
        try:
            filepath = save(uploaded_file)
        except FileSaveError as e:
            return str(e), 400
        expires_in = request.form.get("expiresIn", type=int, default=0)
        expire_time = get_expire_time(expires_in)
        password = request.form.get("password", default="")
        hash = hash_password(password) if password else None
        sql.add_file(uploaded_file.filename, filepath, expire_time, hash)
        return render_template("upload_success.html", filename=uploaded_file.filename, site_url = request.url_root, filepath=filepath)
    return render_template("upload.html", name="Apple")

@app.route("/drop")
def drop():
    if request.method == "POST":
        sql.drop_files()
        return "File table dropped."
    return '''
    <form method="POST">
        <button type="submit">Drop Files</button>
    </form>
    '''


if __name__ == "__main__":
    app.run(debug=True)