import ast
import os
import random
import sys
import time
import traceback
from functools import wraps
from importlib.abc import Loader, PathEntryFinder
from importlib.machinery import FileFinder, ModuleSpec, SourceFileLoader
from types import CodeType
from typing import (
    Any,
    Dict,
    List,
    Mapping,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)
from zlib import crc32

from ._internal import worker_queue
from .collectors.modules import get_pre_init_loaded_modules
from .config import config
from .declarations import Declaration, FileToParse
from .exception_handler import install_exception_handler
from .forkable import register_fork_callbacks
from .instrumentation import instrument_frameworks
from .logging import internal_logger
from .run_mode import should_run_hud
from .utils import calculate_uuid

FunctionDef = TypeVar("FunctionDef", ast.FunctionDef, ast.AsyncFunctionDef)

paths_to_wrap = [
    os.getcwd(),
]  # type: List[str]


def add_path_of_main_module() -> None:
    try:
        spec = getattr(sys.modules["__main__"], "__spec__", None)
        if not spec:
            add_path_of_main_file()
            return

        package = spec.name.split(".")[0]
        package_module = sys.modules.get(package)
        if not package_module:
            add_path_of_main_file()
            return

        package_file = getattr(package_module, "__file__", None)
        if not package_file:
            add_path_of_main_file()
            return

        paths_to_wrap.append(os.path.dirname(os.path.abspath(package_file)))
    except Exception:
        internal_logger.warning("Error while getting main module path", exc_info=True)
        add_path_of_main_file()


def add_path_of_main_file() -> None:
    file_path = getattr(sys.modules["__main__"], "__file__", None)
    if file_path:
        paths_to_wrap.append(os.path.dirname(os.path.abspath(file_path)))


add_path_of_main_module()


class ASTTransformer(ast.NodeTransformer):
    def __init__(self, path: str, code: bytes, file_hash: int) -> None:
        self.path = path
        self.file_hash = file_hash
        self.compiler_flags = 0

    @staticmethod
    def get_and_remove_docstring(
        node: Union[ast.FunctionDef, ast.AsyncFunctionDef],
    ) -> Optional[ast.stmt]:
        """
        If the first expression in the function is a literal string (docstring), remove it and return it
        """

        AstStrType = ast.Constant if sys.version_info >= (3, 8) else ast.Str

        if not node.body:
            return None
        if (
            isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, AstStrType)
            and (
                isinstance(node.body[0].value.value, str)
                if sys.version_info >= (3, 8)
                else isinstance(node.body[0].value.s, str)
            )
        ):
            return node.body.pop(0)
        return None

    @staticmethod
    def get_with_location_from_node(node: FunctionDef) -> Dict[str, int]:
        if len(node.body) == 0:
            return {
                "lineno": node.lineno,
                "col_offset": node.col_offset,
                "end_lineno": getattr(node, "end_lineno", node.lineno),
                "end_col_offset": getattr(node, "end_col_offset", node.col_offset),
            }

        return {
            "lineno": node.body[0].lineno,
            "col_offset": node.body[0].col_offset,
            "end_lineno": getattr(node.body[0], "end_lineno", node.body[0].lineno),
            "end_col_offset": getattr(
                node.body[0], "end_col_offset", node.body[0].col_offset
            ),
        }

    def get_with_stmt(self, function_id: str, node: FunctionDef) -> ast.With:
        locations = self.get_with_location_from_node(node)

        args = [
            ast.Constant(value=function_id, kind=None, **locations)
        ]  # type: List[ast.expr]
        return ast.With(
            items=[
                ast.withitem(
                    context_expr=ast.Call(
                        func=ast.Name(id="HudMonitor", ctx=ast.Load(), **locations),
                        args=args,
                        keywords=[],
                        **locations,
                    ),
                )
            ],
            body=[],
            type_comment=None,
            **locations,
        )

    def _visit_generic_FunctionDef(self, node: FunctionDef) -> FunctionDef:
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

        docstring = self.get_and_remove_docstring(node)

        with_stmt = self.get_with_stmt(str(function_id), node)
        with_stmt.body = node.body

        if not with_stmt.body:
            with_stmt.body = [ast.Pass(**self.get_with_location_from_node(node))]

        if docstring is not None:
            node.body = [docstring, with_stmt]
        else:
            node.body = [with_stmt]

        self.generic_visit(node)
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        return self._visit_generic_FunctionDef(node)

    def visit_AsyncFunctionDef(
        self, node: ast.AsyncFunctionDef
    ) -> ast.AsyncFunctionDef:
        return self._visit_generic_FunctionDef(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Optional[ast.ImportFrom]:
        # When passing an AST to the `compile` function, the `__future__` imports are not parsed
        # and the compiler flags are not set. This is a workaround to set the compiler flags,
        # and removing the invalid imports.
        if node.module == "__future__":
            import __future__

            for name in node.names:
                feature = getattr(__future__, name.name)
                self.compiler_flags |= feature.compiler_flag
            return None

        self.generic_visit(node)
        return node


def should_wrap_file(path: str) -> bool:
    return path in paths_to_wrap


def add_submodule_search_locations(module_name: str) -> None:
    if module_name not in sys.modules:
        return

    module = sys.modules[module_name]
    if (
        hasattr(module, "__spec__")
        and module.__spec__
        and hasattr(module.__spec__, "submodule_search_locations")
        and module.__spec__.submodule_search_locations
    ):
        paths_to_wrap.extend(module.__spec__.submodule_search_locations)


def should_wrap_module(fullname: str) -> bool:
    if fullname in config.modules_to_trace:
        return True
    for module in config.modules_to_trace:
        if fullname.startswith("{}.".format(module)):
            return True
    return False


class MyFileFinder(FileFinder):
    def __repr__(self) -> str:
        return "MyFileFinder('{}')".format(self.path)

    def __init__(
        self,
        path: str,
        *loader_details: Tuple[Type[Loader], List[str]],
        override: bool = False
    ) -> None:
        if not should_wrap_file(os.path.abspath(path)) and not override:
            raise ImportError("Not wrapping path: {}".format(path))

        super().__init__(path, *loader_details)

    def find_spec(self, fullname: str, *args: Any) -> Optional[ModuleSpec]:
        spec = super().find_spec(fullname, *args)
        if spec is not None and spec.submodule_search_locations is not None:
            paths_to_wrap.extend(spec.submodule_search_locations)
        return spec


class ModuleFinder(MyFileFinder):

    def __init__(self, path: str, original_finder: PathEntryFinder) -> None:
        self.path = path
        self.original_finder = original_finder

        if hasattr(original_finder, "_loaders"):
            suffixes = [loader[0] for loader in original_finder._loaders]
        else:
            raise ImportError("Original finder unsupported for path {}".format(path))

        if ".py" not in suffixes:
            raise ImportError("Not wrapping loader that doesn't handle .py files")

        loader_details = []

        if set(suffixes) == {".py"}:
            loader_details.append((MySourceLoader, [".py"]))
        else:
            for suffix, loader in original_finder._loaders:
                if suffix == ".py":
                    loader_details.append((MySourceLoader, [suffix]))
                else:
                    loader_details.append((loader, [suffix]))

        super().__init__(path, *loader_details, override=True)

    def __repr__(self) -> str:
        return "ModuleFinder('{}', original_finder={})".format(
            self.path, self.original_finder
        )

    def find_spec(self, fullname: str, *args: Any) -> Optional[ModuleSpec]:
        spec = None
        if should_wrap_module(fullname):
            spec = super().find_spec(fullname, *args)
        if spec is not None:
            if spec.origin is not None and spec.origin not in paths_to_wrap:
                paths_to_wrap.append(os.path.dirname(spec.origin))
            return spec
        if self.original_finder is not None:
            return self.original_finder.find_spec(fullname, *args)


def hud_pathify(path: str) -> str:
    if config.use_hud_pyc and path.endswith(".py"):
        return path.replace(".py", ".hud.py")
    return path


def hud_unpathify(path: str) -> str:
    if config.use_hud_pyc and path.endswith(".hud.py"):
        return path.replace(".hud.py", ".py")
    return path


class MySourceLoader(SourceFileLoader):
    def path_stats(self, path: str) -> Mapping[str, Any]:
        if config.use_hud_pyc:
            return super().path_stats(hud_unpathify(path))
        else:
            if not path.endswith(".py"):
                return super().path_stats(path)
            stats = super().path_stats(path)
            # This manipulation allows bytecode caching to work for the edited module, without conflicting with the original module
            stats["mtime"] = time.time() * 2 + random.randint(1, 500)  # type: ignore[index]
            return stats

    def get_filename(self, name: Optional[str] = None) -> str:
        path = super().get_filename(name)
        if config.use_hud_pyc:
            return hud_pathify(path)
        return path

    def get_data(self, path: str) -> bytes:
        return super().get_data(hud_unpathify(path))

    def source_to_code(  # type: ignore[override]
        self, data: bytes, path: str, *, _optimize: int = -1
    ) -> CodeType:
        if path and config.use_hud_pyc:
            path = hud_unpathify(path)
        try:
            internal_logger.debug("Monitoring file: {}".format(path))
            tree = cast(
                ast.Module,
                compile(
                    data,
                    path,
                    "exec",
                    flags=ast.PyCF_ONLY_AST,
                    dont_inherit=True,
                    optimize=_optimize,
                ),
            )  # type: ast.Module
            file_hash = crc32(data)
            transformer = ASTTransformer(path, data, file_hash)
            worker_queue.append(FileToParse(path, self.name, file_hash))
            tree = transformer.visit(tree)
            tree.body = [
                *ast.parse("from hud_sdk.native import Monitor as HudMonitor\n").body,
                *tree.body,
            ]

            return cast(
                CodeType,
                compile(
                    tree,
                    path,
                    "exec",
                    flags=transformer.compiler_flags,
                    dont_inherit=True,
                    optimize=_optimize,
                ),
            )
        except Exception:
            internal_logger.error(
                "Error while transforming AST on file",
                data={"path": path},
                exc_info=True,
            )
            return super().source_to_code(data, path)


def _hook_compile_bytecode() -> None:
    if not config.use_hud_pyc:
        return
    from importlib import _bootstrap_external

    original_compile_bytecode = _bootstrap_external._compile_bytecode  # type: ignore[attr-defined]

    @wraps(original_compile_bytecode)
    def hud_compile_bytecode(
        data: Any,
        name: Optional[str] = None,
        bytecode_path: Optional[str] = None,
        source_path: Optional[str] = None,
    ) -> Any:
        if source_path and config.use_hud_pyc:
            source_path = hud_unpathify(source_path)
        return original_compile_bytecode(data, name, bytecode_path, source_path)

    _bootstrap_external._compile_bytecode = hud_compile_bytecode  # type: ignore[attr-defined]


def module_hook(path: str) -> ModuleFinder:
    original_finder = None
    for hook in sys.path_hooks:
        if hook is not module_hook:
            try:
                original_finder = hook(path)
            except ImportError:
                continue
            return ModuleFinder(path, original_finder=original_finder)  # type: ignore[arg-type,unused-ignore]

    raise ImportError("No module finder found for path: {}".format(path))


hook_set = False


def set_hook() -> None:
    try:
        internal_logger.set_component("main")
        with internal_logger.stage_context("set_hook"):
            global hook_set
            if hook_set:
                return

            if not should_run_hud():
                return
            hook_set = True

            start_time = time.time()
            try:
                _set_hook()
            finally:
                internal_logger.info(
                    "Hook set",
                    data={"duration": time.time() - start_time},
                )
    except Exception:
        internal_logger.critical("Error while setting hook", exc_info=True)


def _set_hook() -> None:
    if not config.disable_exception_handler:
        install_exception_handler()

    internal_logger.info("Modules to trace", data={"config": config.modules_to_trace})
    internal_logger.info(
        "Hook stacktrace", data={"stacktrace": traceback.format_stack()}
    )
    worker_queue.append(get_pre_init_loaded_modules())
    _hook_compile_bytecode()
    for path in paths_to_wrap:
        if path in sys.path_importer_cache:
            del sys.path_importer_cache[path]
    for path in sys.path:
        if path in sys.path_importer_cache:
            del sys.path_importer_cache[path]

    loader_details = []
    if hasattr(sys.path_hooks[-1]("."), "_loaders"):
        for suffix, loader in sys.path_hooks[-1](".")._loaders:  # type: ignore[attr-defined]
            if suffix == ".py":
                loader_details.append((MySourceLoader, [suffix]))
            else:
                loader_details.append((loader, [suffix]))

    sys.path_hooks.insert(0, MyFileFinder.path_hook(*loader_details))
    sys.path_hooks.insert(0, module_hook)
    register_fork_callbacks()
    instrument_frameworks()
