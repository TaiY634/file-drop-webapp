from .base import FileStorageBase
import os
from flask import send_file

class LocalFileStorage(FileStorageBase):
    
    def __init__(self, storage_folder: str = "uploads"):
        self.storage_folder = storage_folder
        os.makedirs(self.storage_folder, exist_ok=True)

    def save(self, file: "FileStorage", key: str) -> None:
        filepath = os.path.join(self.storage_folder, key)
        file.save(filepath)

    def download(self, key: str, filename: str | None = None) -> str:
        filepath = os.path.join(self.storage_folder, key)
        if not os.path.exists(filepath):
            raise FileNotFoundError("File not found")
        
        download_filename = filename if filename else key
        return send_file(filepath, as_attachment=True, download_name=download_filename)

    def delete(self, key: str) -> None:
        filepath = os.path.join(self.storage_folder, key)
        if os.path.exists(filepath):
            os.remove(filepath)