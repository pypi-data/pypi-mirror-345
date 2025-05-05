from __future__ import annotations

from pathlib import Path

from .utils import appify
from .utils import try_package
from .utils import unescape_from_var_name


# entry point called by uvicorn to find the async app (i.e out shinyapp)
def __getattr__(name: str) -> object:
    name = unescape_from_var_name(name)
    # maybe we are a module in a package
    name = try_package(name)
    return appify(Path(name))
