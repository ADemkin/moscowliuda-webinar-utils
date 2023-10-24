from typing import Mapping

from aiohttp.web import HTTPFound
from aiohttp.web import HTTPNotFound
from aiohttp.web import Response
from aiohttp.web import View
from aiohttp.web_urldispatcher import UrlDispatcher
from aiohttp.web_urldispatcher import UrlMappingMatchInfo
from aiohttp_jinja2 import template
from yarl import URL

from lib.factory import WebinarTitles
from lib.storage import WebinarStorage
from lib.webinar import Webinar


class BaseView(View):
    @property
    def storage(self) -> WebinarStorage:
        return self.request.app['storage']

    @property
    def router(self) -> UrlDispatcher:
        return self.request.app.router

    @property
    def match_info(self) -> UrlMappingMatchInfo:
        return self.request.match_info

    @property
    def query(self) -> Mapping:
        return dict(self.request.query)


class IndexView(BaseView):
    @template("webinarList.html")
    async def get(self) -> Mapping:
        webinars = self.storage.get_all_webinars()
        return {'webinars': webinars}


class ImportWebinarView(BaseView):
    async def post(self) -> Response:
        form = await self.request.post()
        url = str(form['url'])
        Webinar.from_url(url)  # will raise if something is wrong
        title = WebinarTitles.TEST
        webinar_id = self.storage.add_webinar(url, title)
        location = self.router['webinarView'].url_for(
            webinar_id=str(webinar_id)
        )
        raise HTTPFound(location=location)


class BaseWebinarView(BaseView):
    @property
    def webinar_id(self) -> int:
        webinar_id_str = self.match_info['webinar_id']
        return int(webinar_id_str)

    @property
    def webinar(self) -> Webinar:
        webinar = self.storage.get_webinar_by_id(self.webinar_id)
        if webinar is None:
            raise HTTPNotFound(text='Вебинар не найден')
        return Webinar.from_url(webinar.url)

    def url_for_webinar_view(self, message: str = '') -> URL:
        url = self.router['webinarView'].url_for(
            webinar_id=str(self.webinar_id),
        )
        if message:
            url = url.with_query(message=message)
        return url


class WebinarView(BaseWebinarView):
    @template("webinarView.html")
    async def get(self) -> Mapping:
        webinar = self.storage.get_webinar_by_id(self.webinar_id)
        message = self.query.get('message', None)
        return {
            'webinar': webinar,
            'message': message,
        }


class ImportCertificatesWebinarView(BaseWebinarView):
    async def post(self) -> Mapping:
        self.webinar.certificates_sheet_fill()
        message = 'страница для рассылки создана, проверь её'
        location = self.url_for_webinar_view(message)
        raise HTTPFound(location=location)


class SendEmailsWebinarView(BaseWebinarView):
    async def post(self) -> Mapping:
        self.webinar.send_emails_with_certificates()
        message = 'спам рассылается...'
        location = self.url_for_webinar_view(message)
        raise HTTPFound(location=location)
