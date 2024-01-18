from pathlib import Path

from aiohttp.web import Application
from aiohttp.web import run_app
from aiohttp.web import middleware
from aiohttp.web import Request
from aiohttp.web import Response
from aiohttp.web import HTTPException
from aiohttp.web import Callable
import aiohttp_jinja2
import jinja2

from lib.storage import WebinarStorage
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
            'error': {
                'title': err.__class__.__name__,
                'message': str(err),
            },
        }
        return aiohttp_jinja2.render_template(
            template_name='error.html',
            request=request,
            context=context,
        )


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
    # setup middleware
    app.middlewares.append(handle_exception_middleware)
    # setup storage
    storage = WebinarStorage()
    app['storage'] = storage
    return app


if __name__ == "__main__":
    app = create_app()
    run_app(app, host="localhost", port=8000)
