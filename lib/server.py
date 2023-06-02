import os
from pathlib import Path

from aiohttp.web import Application
from aiohttp.web import run_app
import aiohttp_jinja2
from dotenv import load_dotenv
import jinja2
from loguru import logger

from lib.api import WebinarApi
from lib.storage import DEFAULT_FILE_NAME
from lib.storage import Storage
from lib.views import Webinar
from lib.views import WebinarsList


def create_app() -> Application:
    app = Application()
    # setup routes
    app.router.add_view("/", WebinarsList, name="webinars-list")
    app.router.add_view(r"/{id:\w+}", Webinar, name="webinar")
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
