from __future__ import annotations

import os
import random
from typing import TYPE_CHECKING

from shiny import App
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware


if TYPE_CHECKING:
    from starlette.requests import Request
    from starlette.responses import Response
    from starlette.middleware.base import RequestResponseEndpoint


class StickyCookie(BaseHTTPMiddleware):
    def __init__(self, app: App, value: str, key: str = "sticky") -> None:
        super().__init__(app)
        self.key = key
        self.value = value

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        sticky = request.cookies.get(self.key)
        response = await call_next(request)
        if not sticky:
            response.set_cookie(key=self.key, value=self.value)
        return response


endpoint = os.environ.get("ENDPOINT")


INSTANCE_COOKIE = endpoint if endpoint else f"st-{random.random()}"


def init_sticky(app: App) -> App:
    """Ensure app sends out a "sticky" cookie so it can be identified by nginx"""
    # see hash $cookie_sticky consistent;
    # in templates/sticky.conf
    app.starlette_app.user_middleware.append(
        Middleware(StickyCookie, value=INSTANCE_COOKIE, key="sticky"),
    )
    return app
