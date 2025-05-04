# @Coding: UTF-8
# @Time: 2024/9/25 15:58
# @Author: xieyang_ls
# @Filename: multipart_file.py
import os

import shutil

import tempfile

from typing import Optional

from logging import INFO, error, basicConfig

basicConfig(level=INFO)


class MultipartFile:
    __file_name__: str = None

    __file_bytes__: bytes | None = None

    __temp_file_path__: Optional[str] = None

    def __init__(self, filename: str, file_bytes: bytes):
        self.__file_name__ = filename
        self.__file_bytes__ = file_bytes
        try:
            with tempfile.NamedTemporaryFile(delete=False, mode='wb') as tf:
                tf.write(file_bytes)
                self.__temp_file_path__ = tf.name  # 仅保存路径，不保留文件对象
        except Exception as e:
            self._safe_cleanup()
            raise RuntimeError(f"temp_file is failed: {e}")

    def get_file_name(self) -> str:
        return self.__file_name__

    def get_bytes(self) -> bytes:
        return self.__file_bytes__

    def get_temp_file_path(self) -> str:
        return self.__temp_file_path__

    def copy(self, dest_path: str) -> None:
        if not self.__temp_file_path__:
            raise ValueError("File already closed")
        try:
            shutil.copyfile(self.__temp_file_path__, dest_path)
        except Exception as e:
            raise RuntimeError(f"Copy failed: {e}") from e

    def _safe_cleanup(self) -> None:
        """安全清理临时文件"""
        self.__file_bytes__ = None
        if self.__temp_file_path__ and os.path.exists(self.__temp_file_path__):
            try:
                os.remove(self.__temp_file_path__)
            except Exception as e:
                error(f"Cleanup failed: {e}")
                pass
            self.__temp_file_path__ = None

    def __del__(self) -> None:
        self._safe_cleanup()

    def close(self) -> None:
        self._safe_cleanup()
