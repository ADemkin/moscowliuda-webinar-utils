from aiohttp.web import Application

from lib.webui import views


def setup_routes(app: Application) -> None:
    app.router.add_view(
        path='/',
        handler=views.IndexView,
        name='webinarList',
    )
    app.router.add_view(
        path='/import',
        handler=views.ImportWebinarView,
        name='webinarImport',
    )
    app.router.add_view(
        path='/webinar/{webinar_id}',
        handler=views.WebinarView,
        name='webinarView',
    )
    app.router.add_view(
        path='/webinar/{webinar_id}/importCertificates',
        handler=views.ImportCertificatesWebinarView,
        name='importCertificates',
    )
    app.router.add_view(
        path='/webinar/{webinar_id}/sendEmails',
        handler=views.SendEmailsWebinarView,
        name='sendEmails',
    )
