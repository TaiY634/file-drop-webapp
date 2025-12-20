from abc import ABC, abstractmethod

class FileStorageBase(ABC):
    
    @abstractmethod
    def save(self, file: bytes, key: str) -> None:
        pass

    @abstractmethod
    def download(self, key: str) -> str:
        """returns a flask response that can be passed directly to app.py for downloading"""
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        pass