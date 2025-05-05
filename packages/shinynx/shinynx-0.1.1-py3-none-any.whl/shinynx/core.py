from __future__ import annotations

from uvicorn.importer import import_from_string

from .utils import init_sticky
from .utils import unescape_from_var_name


# entry point called by uvicorn to find the async app (i.e our shinyapp)
def __getattr__(name: str) -> object:
    # e.g. shinynx.core:the.real.app
    name = unescape_from_var_name(name)
    app = import_from_string(name)
    # we need to add some cookie magic to the app
    return init_sticky(app)
