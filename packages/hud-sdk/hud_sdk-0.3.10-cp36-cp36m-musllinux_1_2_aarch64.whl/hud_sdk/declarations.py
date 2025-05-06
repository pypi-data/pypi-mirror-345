import ast
import binascii
import os
import sys
from typing import Any, List, Optional, TypeVar, Union, cast
from uuid import UUID

from .schemas.events import (
    ArgumentType,
    CodeBlockType,
    FunctionArgument,
    FunctionDeclaration,
    ScopeNode,
    ScopeType,
)
from .schemas.schema import Schema
from .utils import calculate_uuid


def parse_function_node_arguments(
    node: Union[ast.FunctionDef, ast.AsyncFunctionDef],
) -> List[FunctionArgument]:
    # We use this specific order to match the order of the arguments in the function signature.
    # paramters look like: (positional_only, /, positional_or_keyword, *varargs, keyword_only, **kwargs),
    # while all of them are optional and can be omitted
    arguments = []
    if hasattr(node.args, "posonlyargs"):  # Added in Python 3.8
        for arg in node.args.posonlyargs:
            arguments.append(FunctionArgument(arg.arg, ArgumentType.POSITIONAL_ONLY))
    for arg in node.args.args:
        arguments.append(FunctionArgument(arg.arg, ArgumentType.ARG))
    if node.args.vararg:
        arguments.append(FunctionArgument(node.args.vararg.arg, ArgumentType.VARARG))
    for arg in node.args.kwonlyargs:
        arguments.append(FunctionArgument(arg.arg, ArgumentType.KEYWORD_ONLY))
    if node.args.kwarg:
        arguments.append(FunctionArgument(node.args.kwarg.arg, ArgumentType.KWARG))
    return arguments


class Declaration:
    __match_args__ = (
        "function_id",
        "name",
        "path",
        "start_line",
        "end_line",
        "is_async",
        "source_code_hash",
        "code_block_type",
        "file_checksum",
    )

    def __init__(
        self,
        function_id: UUID,
        name: str,
        path: str,
        start_line: int,
        end_line: Optional[int],
        is_async: bool,
        source_code_hash: str,
        code_block_type: CodeBlockType,
        file_checksum: int,
        arguments: Optional[List[FunctionArgument]] = None,
        scope: Optional[List[ScopeNode]] = None,
    ):
        self.function_id = function_id
        self.name = name
        self.path = os.path.normpath(path)
        self.start_line = start_line
        self.end_line = end_line
        self.is_async = is_async
        self.source_code_hash = source_code_hash
        self.code_block_type = code_block_type
        self.file_checksum = file_checksum
        self.arguments = arguments or []
        self.scope = scope[:] if scope else []
        self.declarations_count = 0

    @staticmethod
    def get_lineno(
        node: Union[ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef],
    ) -> int:
        if node.decorator_list:
            return node.decorator_list[0].lineno
        return node.lineno

    @classmethod
    def from_function_node(
        cls,
        function_id: UUID,
        node: Union[ast.FunctionDef, ast.AsyncFunctionDef],
        source_code_hash: str,
        path: str,
        is_async: bool,
        scope: List[ScopeNode],
        file_checksum: int,
    ) -> "Declaration":
        return cls(
            function_id,
            node.name,
            path,
            cls.get_lineno(node),
            getattr(node, "end_lineno", None),
            is_async,
            source_code_hash,
            CodeBlockType.FUNCTION,
            file_checksum,
            parse_function_node_arguments(node),
            scope,
        )

    @classmethod
    def from_class_node(
        cls,
        class_id: UUID,
        node: ast.ClassDef,
        source_code_hash: str,
        path: str,
        file_checksum: int,
        scope: List[ScopeNode],
    ) -> "Declaration":
        return cls(
            class_id,
            node.name,
            path,
            cls.get_lineno(node),
            getattr(node, "end_lineno", None),
            False,
            source_code_hash,
            CodeBlockType.CLASS,
            file_checksum,
            None,
            scope,
        )

    @classmethod
    def from_module_node(
        cls,
        module_id: UUID,
        node: ast.Module,
        source_code_hash: str,
        path: str,
        file_checksum: int,
    ) -> "Declaration":
        return cls(
            module_id,
            "<module>",
            path,
            1,
            getattr(node, "end_lineno", None),
            False,
            source_code_hash,
            CodeBlockType.MODULE,
            file_checksum,
            None,
            [],
        )

    def set_declarations_count(self, count: int) -> None:
        self.declarations_count = count

    def for_request(self) -> "FunctionDeclaration":
        return FunctionDeclaration(
            self.path,
            str(self.function_id),
            self.is_async,
            self.name,
            self.source_code_hash,
            self.start_line,
            self.end_line,
            self.code_block_type,
            self.file_checksum,
            self.declarations_count,
            self.arguments,
            self.scope,
        )


class FileToParse(Schema):
    def __init__(self, path: str, module_name: str, file_hash: int) -> None:
        self.path = path
        self.module_name = module_name
        self.file_hash = file_hash


class FilesAggregator:
    def __init__(self) -> None:
        self.files = []  # type: List[FileToParse]

    def add_file(self, declaration: FileToParse) -> None:
        self.files.append(declaration)

    def get_and_clear_files(self) -> List[FileToParse]:
        files = self.files
        self.clear()
        return files

    def clear(self) -> None:
        self.files = []


FunctionDef = TypeVar("FunctionDef", ast.FunctionDef, ast.AsyncFunctionDef)


class ScopeContextManager:
    def __init__(
        self,
        scope: List[ScopeNode],
        node: Union[ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module],
        default_name: str = "",
    ) -> None:
        self.default_name = default_name
        self.scope = scope
        self.node = node

    def __enter__(self) -> None:
        if isinstance(self.node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            scope_type = ScopeType.FUNCTION
        elif isinstance(self.node, ast.ClassDef):
            scope_type = ScopeType.CLASS
        elif isinstance(self.node, ast.Module):
            scope_type = ScopeType.MODULE
        else:
            raise TypeError("Invalid node type")

        self.scope.append(
            ScopeNode(scope_type, getattr(self.node, "name", self.default_name))
        )

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.scope.pop()


class DeclarationVisitor(ast.NodeVisitor):
    def __init__(
        self, path: str, module_name: str, code: bytes, file_hash: int
    ) -> None:
        self.path = path
        self.module_name = module_name
        self.file_hash = file_hash
        self.lines = code.splitlines()
        self.compiler_flags = 0
        self.scope = []  # type: List[ScopeNode]
        self.declarations = []  # type: List[Declaration]

    def get_declarations(self) -> List[Declaration]:
        for declaration in self.declarations:
            declaration.set_declarations_count(len(self.declarations))
        return self.declarations

    def get_function_source_code_hash(
        self, node: Union[ast.stmt, ast.expr, ast.mod]
    ) -> str:
        if (sys.version_info.major, sys.version_info.minor) < (3, 8):
            return binascii.crc32(ast.dump(node).encode()).to_bytes(4, "big").hex()
        else:
            start_line = getattr(node, "lineno", 1) - 1
            end_line = cast(int, getattr(node, "end_lineno", 1)) - 1
            source_code = b"\n".join(self.lines[start_line : end_line + 1])
            return binascii.crc32(source_code).to_bytes(4, "big").hex()

    def scope_manager(
        self,
        node: Union[ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module],
        default_name: str = "",
    ) -> ScopeContextManager:
        return ScopeContextManager(self.scope, node, default_name)

    def _visit_generic_FunctionDef(self, node: FunctionDef) -> FunctionDef:
        source_code_hash = self.get_function_source_code_hash(node)
        function_id = calculate_uuid(
            "|".join(
                (
                    node.name,
                    self.path,
                    str(Declaration.get_lineno(node)),
                    str(self.file_hash),
                )
            )
        )

        if isinstance(node, ast.FunctionDef):
            is_async = False
        elif isinstance(node, ast.AsyncFunctionDef):
            is_async = True
        else:
            raise TypeError("Invalid node type")

        self.declarations.append(
            Declaration.from_function_node(
                function_id,
                node,
                source_code_hash,
                self.path,
                is_async,
                self.scope,
                self.file_hash,
            )
        )

        with self.scope_manager(node):
            self.generic_visit(node)
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        return self._visit_generic_FunctionDef(node)

    def visit_AsyncFunctionDef(
        self, node: ast.AsyncFunctionDef
    ) -> ast.AsyncFunctionDef:
        return self._visit_generic_FunctionDef(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        source_code_hash = self.get_function_source_code_hash(node)
        class_id = calculate_uuid(
            "{}|{}|{}".format(node.name, self.path, Declaration.get_lineno(node))
        )
        self.declarations.append(
            Declaration.from_class_node(
                class_id,
                node,
                source_code_hash,
                self.path,
                self.file_hash,
                self.scope,
            )
        )
        with self.scope_manager(node):
            self.generic_visit(node)
            return node

    def visit_Module(self, node: ast.Module) -> Any:
        source_code_hash = self.get_function_source_code_hash(node)
        module_id = calculate_uuid(self.path)
        self.declarations.append(
            Declaration.from_module_node(
                module_id, node, source_code_hash, self.path, self.file_hash
            )
        )

        with self.scope_manager(node, default_name=self.module_name):
            self.generic_visit(node)
            return node
