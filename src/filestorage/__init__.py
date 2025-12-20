from .localfs import LocalFileStorage
from .s3 import S3FileStorage

def get_filestorage(*, local: bool) -> 'FileStorageBase':
    if local:
        return LocalFileStorage()
    else:
        return S3FileStorage()