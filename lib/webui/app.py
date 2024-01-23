from pathlib import Path

import aiohttp_jinja2
import jinja2
from aiohttp.web import Application
from aiohttp.web import Callable
from aiohttp.web import HTTPException
from aiohttp.web import Request
from aiohttp.web import Response
from aiohttp.web import middleware
from aiohttp.web import run_app

from lib.domain.webinar.service import WebinarService
from lib.webui.routes import setup_routes

CWD = Path(".")


@middleware
async def handle_exception_middleware(
    request: Request,
    handler: Callable,
) -> Response:
    try:
        return await handler(request)
    except HTTPException as err:
        raise err
    except Exception as err:
        context = {
            "error": {
                "title": err.__class__.__name__,
                "message": str(err),
            },
        }
        return aiohttp_jinja2.render_template(
            template_name="error.html",
            request=request,
            context=context,
        )


def create_app() -> Application:
    application = Application()
    # setup routes
    setup_routes(application)
    # setup templates
    templates_dir = CWD / "lib" / "templates"
    aiohttp_jinja2.setup(
        app=application,
        loader=jinja2.FileSystemLoader(templates_dir),
    )
    # setup middleware
    application.middlewares.append(handle_exception_middleware)
    # setup services and repositories
    application["webinar_service"] = WebinarService()
    return application


if __name__ == "__main__":
    app = create_app()
    run_app(app, host="localhost", port=8000)
