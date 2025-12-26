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
                'password_hash': str(password_hash),
                'tokens': self.TOKEN_CAP,
                'token_cap': self.TOKEN_CAP,
                'last_token_refill': 0,
                'token_increment_interval': self.TOKEN_INCREMENT_INTERVAL
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
                'password_hash': item['password_hash'],
                'tokens': item['tokens'],
                'token_cap': item['token_cap'],
                'last_token_refill': item['last_token_refill'],
                'token_increment_interval': item['token_increment_interval']
            }
        return {}

    def refill_tokens(self, file_id, count, update_time):
        if count <= 0:
            return
        response = self.table.get_item(Key={'file_id': file_id})
        item = response.get('Item')
        if not item:
            return
        tokens = item['tokens']
        token_cap = item['token_cap']
        if count > 0:
            new_tokens = min(token_cap, tokens + count)
            self.table.update_item(
                Key={'file_id': file_id},
                UpdateExpression='SET tokens = :tokens, last_token_refill = :last_token_refill',
                ExpressionAttributeValues={
                    ':tokens': new_tokens,
                    ':last_token_refill': update_time
                }
            )

    def consume_token(self, file_id: str, count: int = 1) -> bool:  
        response = self.table.get_item(Key={'file_id': file_id})
        item = response.get('Item')
        if not item:
            return False
        tokens = item['tokens']
        if tokens >= count:
            new_tokens = tokens - count
            self.table.update_item(
                Key={'file_id': file_id},
                UpdateExpression='SET tokens = :tokens',
                ExpressionAttributeValues={
                    ':tokens': new_tokens
                }
            )
            return True
        return False
    
    def has_enough_token(self, file_id, count):
        response = self.table.get_item(Key={'file_id': file_id})
        item = response.get('Item')
        if not item:
            return False
        tokens = item['tokens']
        return tokens >= count