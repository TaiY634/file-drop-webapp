from abc import ABC, abstractmethod

class DatabaseBase(ABC):
    """
    Each item in the table should have:
        file_id: str (uuid) **primary key**
        filename: str
        key: str (storage key)
        expire_at: int (time since epoch)
        downloads: int
        attempts: int
        password_hash: str | None
    """
    # (file_id, filename, key, expire_at, downloads, attempts, password_hash)

    @abstractmethod
    def create(self, file_id: str, filename: str, key: str, expire_at: int, downloads: int, attempts: int, password_hash: str) -> None:
        pass

    @abstractmethod
    def get(self, file_id: str) -> dict:
        pass

    @abstractmethod
    def increment_downloads(self, file_id: str) -> None:
        pass

    @abstractmethod
    def increment_attempts(self, file_id: str) -> None:
        pass
