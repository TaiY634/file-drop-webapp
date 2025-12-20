from .sqlite import SQLiteMetadata, IntegrityError
from .dynamodb import DynamoDBMetadata

class DuplicateIDError(Exception):
    pass

def get_database(*, local: bool, **kwargs):
    if local:
        try:
            return SQLiteMetadata(**kwargs)
        except IntegrityError as e:
            if 'UNIQUE constraint failed' in str(e):
                raise DuplicateIDError from e
            else:
                raise
    else:
        return DynamoDBMetadata(**kwargs)