import os

import pendulum
from fastapi import UploadFile
from fastapi.responses import FileResponse

from config.logger import log
from services.storage.abstract_client import ClientInterface
from services.storage.local_client import LocalClient
from utils.enum import BaseEnum


def get_client() -> ClientInterface:
    return LocalClient()


class FileTypeEnum(BaseEnum):
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    DOCUMENT = "document"


class Helper:
    def __init__(self, client: ClientInterface = get_client()) -> None:
        self.client = client

    async def upload(self, file: UploadFile, filename: str = "", context: str = "") -> str:
        log.debug(f"<Filehelper upload_file> init with filename {filename} context {context}\n")
        if context: context = await self._clean_path(context)
        if filename:
            filename = await self._clean_path(filename, trailing_slash=False)
            filename += os.path.splitext(file.filename)[-1]
        else:
            filename = await self._clean_path(file.filename, trailing_slash=False)

        log.debug(f"<Filehelper upload_file post clean> filename {filename} context {context}")

        root, extension = os.path.splitext(filename)
        timestamp = str(pendulum.now().timestamp()).replace('.', '')
        filename = f"{root.split('.')[0]}_{timestamp}{extension}"
        filepath = context + filename
        log.debug(f"<Filehelper upload_file post timestamp> filename {filename} filepath {filepath}")

        result = await self.client.upload(file=file, filename=filepath)
        log.debug(f"<Filehelper upload_file> exit")
        return result

    async def get(self, path) -> FileResponse | bytes:
        return await self.client.get(path)

    async def rename(self, path: str, new_name: str) -> str:
        return await self.client.rename(path, new_name)

    async def move(self, src: str, dest: str) -> str:
        return await self.client.move(src=src, dest=dest)

    async def delete(self, path: str):
        return await self.client.delete(path=path)

    async def get_bytes(self, path) -> bytes:
        return await self.client.get(path=path)

    @staticmethod
    async def _clean_path(path: str, trailing_slash=True) -> str | None:
        if not path: return None
        path = path.replace('\\', '/')

        path_parts = path.strip().split('/')
        cleaned_parts = [part for part in path_parts if part]
        cleaned_path = '/'.join(cleaned_parts)
        if trailing_slash and cleaned_path and not cleaned_path.endswith('/'):
            cleaned_path += '/'
        return cleaned_path

    @staticmethod
    async def get_mime(file: UploadFile) -> str:
        """
        Accepts a file as bytes, BinaryIO (e.g., file-like object), or UploadFile.
        Tries to guess the file mimetype.
        """
        import filetype

        await file.seek(0)
        content = await file.read()
        await file.seek(0)

        return filetype.guess_mime(content)
