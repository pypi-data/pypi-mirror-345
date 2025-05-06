def format_path_declaration(path: str) -> str:
    return _fix_slash(path)


def format_path_metric(path: str) -> str:
    path = _fix_slash(path)
    path = _remove_query_params(path)
    return path


def _remove_query_params(path: str) -> str:
    return path.split("?")[0]


def _fix_slash(path: str) -> str:
    if path.endswith("/"):
        path = path[:-1]
    if not path.startswith("/"):
        path = "/" + path
    return path


def strip_regex(route: str) -> str:
    return route.lstrip("^").rstrip("$")
