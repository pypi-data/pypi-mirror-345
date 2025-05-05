from __future__ import annotations

import importlib.util
import os
import platform
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from typing import Callable
from typing import TYPE_CHECKING

from shiny.express import wrap_express_app

from .sticky import init_sticky

if TYPE_CHECKING:
    from shiny import App
    from starlette.requests import Request


def appify(express_py_file: Path) -> App:
    """Turn an Express app file into an App"""
    app = wrap_express_app(express_py_file)
    return init_sticky(app)


def add_route(
    app: App,
    path: str,
    func: Callable[[Request], Any],
    name: str | None = None,
) -> None:
    """See also https://shiny.posit.co/py/docs/routing.html."""
    from starlette.routing import Route

    route = Route(path, func, name=name)
    # need to insert this! Can't append! so add_route can't work.
    app.starlette_app.router.routes.insert(0, route)


@dataclass
class Runner:
    cmd: list[str]
    directory: str = "."
    env: dict[str, str] | None = None

    def getenv(self) -> dict[str, str] | None:
        if not self.env:
            return None
        return self.env  # return {**os.environ, **self.env}

    def start(self) -> subprocess.Popen[bytes]:

        return subprocess.Popen(
            self.cmd,
            cwd=self.directory,
            env=self.getenv(),
            shell=False,
        )


def run_app(
    app: str,
    *,
    workers: int = 3,
    working_dir: str = ".",
    log_level: str = "info",
    express: bool = False,
    socket_name: str = "app{n}.sock",
    uvicornargs: tuple[str, ...] = (),
) -> None:
    if not express:
        # a/b/c.py, '.' -> c:app, './a/b'
        app, working_dir = resolve_app(app, working_dir)
    app = app_to_uvicorn_app(app, express=express)

    procs = []
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "--loop=asyncio",
        "--lifespan=on",
        f"--log-level={log_level}",
        *uvicornargs,
        "--uds",
    ]
    # Don't allow shiny to use uvloop! (see _main.py)
    # https://github.com/posit-dev/py-shiny/issues/1373
    for n in range(1, workers + 1):
        socket = socket_name.format(n=n)
        runner = Runner(
            [
                *cmd,
                socket,
                app,
            ],
            env=dict(ENDPOINT=socket),
            directory=working_dir,
        )
        procs.append(runner)

    shinpy_apps = [p.start() for p in procs]

    try:
        for proc in shinpy_apps:
            proc.wait()

    except KeyboardInterrupt:
        for proc in shinpy_apps:
            proc.wait(0.5)


def app_to_uvicorn_app(app: str, express: bool = False) -> str:
    if express:
        ret = f"shinynx.express:{escape_to_var_name(app)}"
    else:
        if ":" not in app:
            app += ":app"
        ret = f"shinynx.core:{escape_to_var_name(app)}"
    return ret


def try_package(name: str) -> str:
    try:
        module = importlib.util.find_spec(name, None)
        if module is None or module.origin is None or not module.has_location:
            return name
        return module.origin
    except (ModuleNotFoundError, ImportError):
        # find_spec throws ImportError when the module starts with "."
        return name


# taken from shiny.express._utils.py
# we could just import these functions but they are internal
# so might disappear|move


def escape_to_var_name(x: str) -> str:
    """
    Given a string, escape it to a valid Python variable name which contains
    [a-zA-Z0-9_]. All other characters will be escaped to _<hex>_. Also, if the first
    character is a digit, it will be escaped to _<hex>_, because Python variable names
    can't begin with a digit.
    """
    if not x:
        return x

    encoded = []

    if re.match("[0-9]", x[0]):
        encoded.append(f"_{ord(x[0]):x}_")
        x = x[1:]

    for char in x:
        if re.match("[a-zA-Z0-9]", char):
            encoded.append(char)
        else:
            encoded.append(f"_{ord(char):x}_")

    return "".join(encoded)


def unescape_from_var_name(x: str) -> str:
    """
    Given a string that was escaped to a Python variable name, unescape it -- that is,
    convert it back to a regular string.
    """

    def replace_func(match: re.Match[str]) -> str:
        return chr(int(match.group(1), 16))

    return re.sub("_([a-zA-Z0-9]+)_", replace_func, x)


def resolve_app(app: str, app_dir: str) -> tuple[str, str]:

    def is_file(m: str) -> bool:
        return "/" in m or "\\" in m or m.endswith(".py")

    # The `app` parameter can be:
    #
    # - A module:attribute name
    # - An absolute or relative path to a:
    #   - .py file (look for app inside of it)
    #   - directory (look for app:app inside of it)
    # - A module name (look for :app) inside of it

    if platform.system() == "Windows" and re.match("^[a-zA-Z]:[/\\\\]", app):
        # On Windows, need special handling of ':' in some cases, like these:
        #   shiny run c:/Users/username/Documents/myapp/app.py
        #   shiny run c:\Users\username\Documents\myapp\app.py
        module, attr = app, ""
    else:
        module, _, attr = app.partition(":")
    if not module:
        raise ImportError("The APP parameter cannot start with ':'.")
    if not attr:
        attr = "app"

    if is_file(module):
        module_path = os.path.join(app_dir, module)
        dirname, filename = os.path.split(module_path)
        module = filename[:-3] if filename.endswith(".py") else filename
        app_dir = dirname

    return f"{module}:{attr}", app_dir
