from abc import ABC, abstractmethod

class DatabaseBase(ABC):
    """
    Each item in the table should have:
        file_id: str (uuid) **primary key**
        filename: str
        key: str (storage key)
        expire_at: int (time since epoch)
        password_hash: str | None
        tokens: int
        token_cap: int:
        last_token_refill: int (time since epoch)
        token_increment_interval: int (seconds)
    """
    # (file_id, filename, key, expire_at, downloads, attempts, password_hash)

    TOKEN_CAP = 100
    TOKEN_INCREMENT_INTERVAL = 5  # seconds

    @abstractmethod
    def create(self, file_id: str, filename: str, key: str, expire_at: int) -> None:
        pass

    @abstractmethod
    def get(self, file_id: str) -> dict:
        pass

    @abstractmethod
    def refill_tokens(self, file_id: str, count: int, update_time: int) -> None:
        """
        Refill tokens for the given file_id based on the given count.
        Should not exceed token_cap.
        This method should be called before any operation that consumes tokens.
        """
        pass

    @abstractmethod
    def consume_token(self, file_id: str, count: int = 1) -> bool:
        """
        Consume token(s) for the given file_id.
        Returns True if a token was successfully consumed, False if no tokens are available.
        """
        pass

    @abstractmethod
    def has_enough_token(self, file_id: str, count: int) -> bool:
        """
        Check if there are enough tokens available for the given file_id.
        Returns True if enough tokens are available, False otherwise.
        """
        pass
