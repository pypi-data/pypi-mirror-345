import ast
import asyncio
import os
from typing import Dict, List, Set, cast
from zlib import crc32

from ..client import AsyncHandlerReturnType, Client
from ..declarations import Declaration, DeclarationVisitor, FileToParse
from ..logging import internal_logger
from ..schemas.events import FileDeclaration
from ..schemas.responses import FileDeclarations as FileDeclarationsResponse
from .loop_utils import run_in_thread


async def process_file_declarations(
    files: Set[FileToParse],
    client: Client[AsyncHandlerReturnType],
    loop: asyncio.AbstractEventLoop,
) -> None:
    file_to_decl_map: Dict[FileToParse, FileDeclaration] = {}
    for file in files:
        file_path_checksum = crc32(os.path.normpath(file.path).encode())
        file_checksum = file.file_hash
        file_decl = FileDeclaration(file_path_checksum, file_checksum)
        file_to_decl_map[file] = file_decl

    unique_file_decls = sorted(
        file_to_decl_map.values(),
        key=lambda fd: f"{fd.file_path_checksum}|{fd.file_checksum}",
    )

    try:
        file_declarations_response: FileDeclarationsResponse = (
            await client.send_file_declarations(unique_file_decls)
        )
    except Exception:
        internal_logger.exception("Failed to send file declarations")
        files_to_process = list(files)
    else:
        if file_declarations_response.send_all:
            files_to_process = list(files)
        else:
            wanted_set = set(file_declarations_response.files)
            files_to_process = [
                file for file in files if file_to_decl_map[file] in wanted_set
            ]

    declarations_to_send: List[Declaration] = []
    for file in files_to_process:
        file_decls = await run_in_thread(loop, _process_file, file)
        declarations_to_send.extend(file_decls)

    if declarations_to_send:
        function_declarations = [d.for_request() for d in declarations_to_send]
        await client.send_batch_json(function_declarations, "FunctionDeclaration")


def _process_file(file: FileToParse) -> List[Declaration]:
    try:
        with open(file.path, "rb") as f:
            content = f.read()
        tree = cast(
            ast.Module,
            compile(
                content,
                file.path,
                "exec",
                flags=ast.PyCF_ONLY_AST,
                dont_inherit=True,
                optimize=-1,
            ),
        )
        transformer = DeclarationVisitor(
            file.path, file.module_name, content, file.file_hash
        )
        transformer.visit(tree)
        return transformer.get_declarations()
    except Exception:
        internal_logger.exception("Failed to process file", data={"file": file})
        return []
