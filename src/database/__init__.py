from .sqlite import SQLiteMetadata
from .dynamodb import DynamoDBMetadata
from sqlite3 import IntegrityError


def get_database(*, local: bool, **kwargs):
    if local:
        return SQLiteMetadata(**kwargs)
    else:
        return DynamoDBMetadata(**kwargs)