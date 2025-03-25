import os
from shutil import copyfile, move

from fastapi import HTTPException, UploadFile
from fastapi.responses import FileResponse
from starlette import status

from config.logger import log
from config.settings import settings
from services.storage.abstract_client import ClientInterface
from utils.exceptions.exc_500 import http_500_exc_internal_server_error


class LocalClient(ClientInterface):
    client_name = "local"

    @classmethod
    async def get(cls, path, raw: bool = False) -> FileResponse | bytes:
        if not os.path.exists(path):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File not found")
        if not raw:
            return FileResponse(str(path), filename=path.split("/")[-1])
        with open(path, "rb") as f:
            file = f.read()
        return file

    @classmethod
    async def upload(cls, file: UploadFile, filename: str) -> str:
        file_location = os.path.join(settings.UPLOAD_ROOT, filename)
        os.makedirs(os.path.dirname(file_location), exist_ok=True)
        with open(file_location, "wb") as file_object:
            file_object.write(file.file.read())
        # file_location = cls._append_domain_name(file_location)
        file_location = file_location.replace("\\", "/")
        return file_location

    @classmethod
    async def delete(cls, path: str) -> None:
        # cls._strip_domain_name(filepath)
        if os.path.exists(path):
            os.remove(path)
        else:
            # raise HTTPException(status_code=404, detail="File not found")
            pass

    @classmethod
    async def copy(cls, src: str, dest: str) -> str:
        # Convert paths to absolute paths and normalize them
        src = os.path.abspath(src)
        filename = os.path.basename(src)

        file_dest = os.path.abspath(os.path.join(settings.UPLOAD_ROOT, dest.lstrip('/')))
        abs_dest = os.path.join(file_dest, filename)

        if os.path.exists(src):
            try:
                os.makedirs(file_dest, exist_ok=True)
                copyfile(src, abs_dest)
                return abs_dest
            except PermissionError:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied while copying file"
                )
            except:
                log.exception(f"Failed to copy file from {src} to {dest}")
                raise await http_500_exc_internal_server_error()
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Source file not found: {src}"
            )

    @classmethod
    async def rename(cls, path: str, new_name: str) -> str:
        src = os.path.abspath(path)
        ext = os.path.basename(src).split(".")[-1]

        directory = os.path.dirname(src)
        new_path = os.path.join(directory, new_name) + f".{ext}"

        if os.path.exists(src):
            try:
                os.rename(src, new_path)
                return new_path
            except PermissionError:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied while renaming file"
                )
            except:
                raise await http_500_exc_internal_server_error()
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Source file not found: {src}"
            )

    @classmethod
    async def move(cls, src: str, dest: str) -> str:
        src = os.path.abspath(src)
        filename = os.path.basename(src)

        file_dest = os.path.abspath(os.path.join(settings.UPLOAD_ROOT, dest.lstrip('/')))
        os.makedirs(file_dest, exist_ok=True)
        abs_dest = os.path.join(file_dest, filename)

        if os.path.exists(src):
            try:
                real_dest = move(src, abs_dest)
                return real_dest
            except:
                log.exception(f"Failed to move {src} to {abs_dest}")
                raise await http_500_exc_internal_server_error()
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Source file not found"
            )

    @staticmethod
    async def _strip_domain_name(path: str) -> str:
        path = path.replace(f"{settings.APP_DOMAIN}/", "")
        return path

    @staticmethod
    async def _append_domain_name(path: str) -> str:
        log.debug(f"path: {path}")
        if settings.APP_DOMAIN:
            path = settings.APP_DOMAIN + path
            log.debug(f"path with domain: {path}")
        return path
