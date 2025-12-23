from .base import DatabaseBase
import boto3
from botocore.exceptions import ClientError
from helpers.custom_exceptions import DuplicateIDError

class DynamoDBMetadata(DatabaseBase):
    def __init__(self, table_name: str = "file-drop-metadata", region_name: str = "us-east-1"):
        dynamodb = boto3.resource('dynamodb', region_name=region_name)
        self.table = dynamodb.Table(table_name)

    # (file_id, filename, key, expire_at, downloads, attempts, password_hash)


    def create(self, file_id: str, filename: str, key: str, expire_at: int, downloads: int, attempts: int, password_hash: str) -> None:
        item = {
                'file_id': file_id,
                'filename': filename,
                'key': key,
                'expire_at': expire_at,
                'downloads': downloads,
                'attempts': attempts,
                'password_hash': str(password_hash)
            }
        try:
            self.table.put_item(
                Item=item,
                ConditionExpression='attribute_not_exists(file_id)'
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise DuplicateIDError from e
            else:
                raise

    def get(self, file_id: str) -> dict:
        response = self.table.get_item(Key={'file_id': file_id})
        item = response.get('Item')
        if item:
            return {
                'file_id': item['file_id'],
                'filename': item['filename'],
                'key': item['key'],
                'expire_at': item['expire_at'],
                'downloads': item['downloads'],
                'attempts': item['attempts'],
                'password_hash': item['password_hash']
            }
        return {}

    def increment_downloads(self, file_id: str) -> None:
        self.table.update_item(
            Key={'file_id': file_id},
            UpdateExpression='SET downloads = downloads + :inc',
            ExpressionAttributeValues={':inc': 1}
        )

    def increment_attempts(self, file_id: str) -> None:
        self.table.update_item(
            Key={'file_id': file_id},
            UpdateExpression='SET attempts = attempts + :inc',
            ExpressionAttributeValues={':inc': 1}
        )