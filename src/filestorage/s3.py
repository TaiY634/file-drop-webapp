from .base import FileStorageBase
from flask import redirect
import boto3

class S3FileStorage(FileStorageBase):
    def __init__(self, bucket_name: str = "file-drop-uploads", region_name: str = "us-east-1"):
        self.s3 = boto3.client("s3",  region_name=region_name)
        self.bucket_name = bucket_name


    def save(self, file: "FileStorage", key: str) -> None:
        self.s3.upload_fileobj(file, self.bucket_name, key)

    def download(self, key: str, filename: str | None = None) -> str:
        presigned_url = self.s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket_name, 'Key': key},
            ExpiresIn=5  # URL valid for 5 seconds
        )
        return redirect(presigned_url)
    
    def delete(self, key: str) -> None:
        self.s3.delete_object(Bucket=self.bucket_name, Key=key)