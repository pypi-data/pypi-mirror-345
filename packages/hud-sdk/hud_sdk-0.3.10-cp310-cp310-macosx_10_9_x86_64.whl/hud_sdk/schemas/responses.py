from typing import List

from .events import FileDeclaration
from .schema import JSON, Schema


class FileDeclarations(Schema):

    def __init__(self, files: List[FileDeclaration], send_all: bool):
        self.files: List[FileDeclaration] = files
        self.send_all = send_all

    @staticmethod
    def from_json_data(data: JSON) -> "FileDeclarations":
        if not isinstance(data, dict):
            raise ValueError("Invalid data")

        files = data.get("files")
        send_all = data.get("send_all")
        if not isinstance(files, list) or not isinstance(send_all, bool):
            raise ValueError("Invalid data")

        return FileDeclarations(
            files=[FileDeclaration.from_json_data(file) for file in files],
            send_all=send_all,
        )
