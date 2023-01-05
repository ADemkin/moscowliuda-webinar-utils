import os
from pathlib import Path

import aiohttp_jinja2
import jinja2
from aiohttp.web import Application, run_app
from dotenv import load_dotenv
from loguru import logger

from api import WebinarApi
from storage import DEFAULT_FILE_NAME, Storage
from views import Webinar, WebinarsList


def create_app() -> Application:
    app = Application()
    # setup routes
    app.router.add_view("/", WebinarsList, name="webinars-list")
    app.router.add_view("/{id}", Webinar, name="webinar")
    # setup templates
    aiohttp_jinja2.setup(
        app=app,
        loader=jinja2.FileSystemLoader(Path("templates")),
    )
    # setup custom objects
    storage = Storage.from_path(Path(DEFAULT_FILE_NAME))
    api = WebinarApi(storage)
    app["api"] = api
    return app


async def acreate_app() -> Application:
    """Async version for app factory for gunicorn"""
    return create_app()


def main() -> None:
    load_dotenv()
    host = os.environ.get("HOST", "localhost")
    port = int(os.environ.get("PORT", "8080"))
    logger.info(f"Server started on {host}:{port}")
    app = create_app()
    run_app(app, host=host, port=port)


if __name__ == "__main__":
    main()
