from pathlib import Path

from aiohttp.web import Application
from aiohttp.web import RouteTableDef
from aiohttp.web import run_app
import aiohttp_jinja2
import jinja2

from lib.storage import WebinarStorage
from lib.webui.routes import setup_routes

CWD = Path(".")
routes = RouteTableDef()


def create_app() -> Application:
    app = Application()
    # setup routes
    setup_routes(app)
    # setup templates
    templates_dir = CWD / "lib" / "templates"
    aiohttp_jinja2.setup(
        app=app,
        loader=jinja2.FileSystemLoader(templates_dir),
    )
    storage = WebinarStorage()
    app['storage'] = storage
    return app


if __name__ == "__main__":
    app = create_app()
    run_app(app, host="localhost", port=8000)
