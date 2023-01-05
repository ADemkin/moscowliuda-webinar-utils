from abc import abstractmethod
from functools import cached_property, partial
from typing import Any, Mapping

from aiohttp.web import Response, View
from aiohttp_jinja2 import render_template

from api import WebinarApi


class BaseView(View):
    ctx: dict[str, Any] = {}

    @abstractmethod
    @property
    def template(self) -> str:
        ...

    @cached_property
    def api(self) -> WebinarApi:
        return self.request.app["api"]

    @property
    def query(self) -> Mapping[str, str]:
        return dict(self.request.match_info)

    def render(self) -> Response:
        return partial(
            render_template,
            self.template,
            self.request,
            self.ctx,
        )()

    async def form(self) -> Mapping[str, Any]:
        return dict(await self.request.post())


class WebinarsList(BaseView):
    template = "webinars_list.html"

    async def get(self) -> Response:
        self.ctx["webinars"] = self.api.list_webinars()
        return self.render()

    async def post(self) -> Response:
        url = (await self.post())["url"]
        self.api.import_webinar_from_url(url)
        return await self.get()


class Webinar(BaseView):
    template = "webinar.html"

    async def get(self) -> Response:
        webinar_id = self.query.get("id", "not-existing-webinar-id")
        if webinar := self.api.get_webinar(webinar_id):
            self.ctx["webinar"] = webinar
        else:
            self.ctx["error"] = "Webinar not found"
        return self.render()
