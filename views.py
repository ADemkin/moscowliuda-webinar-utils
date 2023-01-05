from functools import cached_property
from typing import Any

from aiohttp.web import Response, View
from aiohttp_jinja2 import render_template

from api import WebinarApi


class BaseView(View):
    template = "base.html"

    @cached_property
    def api(self) -> WebinarApi:
        return self.request.app["api"]


class WebinarsList(BaseView):
    template = "webinars_list.html"

    async def get(self) -> Response:
        webinars = self.api.list_webinars()
        ctx = {"webinars": webinars}
        return render_template(self.template, self.request, ctx)

    async def post(self) -> Response:
        form = await self.request.post()
        url = str(form["url"])
        self.api.import_webinar_from_url(url)
        return await self.get()


class Webinar(BaseView):
    template = "webinar.html"

    async def get(self) -> Response:
        ctx: dict[str, Any] = {}
        try:
            webinar_id = str(self.request.match_info["id"])
        except KeyError:
            ctx["error"] = "Webinar not found"
            return render_template(self.template, self.request, ctx)
        webinar = self.api.get_webinar(webinar_id)
        if not webinar:
            ctx["error"] = "Webinar not found"
            return render_template(self.template, self.request, ctx)
        ctx = {"webinar": webinar}
        return render_template(self.template, self.request, ctx)
