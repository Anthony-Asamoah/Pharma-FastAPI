from abc import ABC, abstractmethod

from fastapi import UploadFile
from starlette.responses import FileResponse


class ClientInterface(ABC):
    client_name = "abstract"

    @classmethod
    @abstractmethod
    async def get(cls, path) -> FileResponse | bytes:
        """
        Retrieve a file given its filepath.
        """
        raise NotImplementedError("Method not implemented")

    @classmethod
    async def upload(cls, file: UploadFile, filename: str) -> str:
        """
        Save the file and return the filepath as string
        """
        raise NotImplementedError("Method not implemented")

    @classmethod
    @abstractmethod
    async def delete(cls, path: str) -> None:
        """
        Delete a file given its filepath.
        """
        raise NotImplementedError("Method not implemented")

    @classmethod
    @abstractmethod
    async def copy(cls, src: str, dest: str) -> str:
        """
        Copy a file from source path to destination path.
        """
        raise NotImplementedError("Method not implemented")

    @classmethod
    @abstractmethod
    async def move(cls, src: str, dest: str) -> str:
        """
        Move a file from source path to destination path.
        """
        raise NotImplementedError("Method not implemented")

    @classmethod
    @abstractmethod
    async def rename(cls, path: str, new_name: str) -> str:
        """
        Change a file name.
        """
        raise NotImplementedError("Method not implemented")
