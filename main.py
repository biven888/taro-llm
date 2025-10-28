import threading
from aiohttp import web
import jinja2
import aiohttp_jinja2

from settings import settings
from app.routes import setup_routes as setup_magic_routes
from mcp_server.server import mcp


application = web.Application()


def setup_templates(app: web.Application) -> None:
    '''
    Интеграция шаблонов Jinja2

    :param app: приложение, для которого интегрируем шаблоны
    :type app: Application
    :return:
    :rtype: None
    '''

    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(f'{settings.BASE_DIR}/app/templates'))


def setup_routes(app: web.Application) -> None:
    '''
    Добавление статических файлов и настройка путей

    :param app: приложение, для которого настраиваем пути
    :type app: Application
    :return:
    :rtype: None
    '''

    app.router.add_static('/static/', path=f'{settings.BASE_DIR}/app/static/')
    setup_magic_routes(app)


def setup_app(app: web.Application) -> None:
    '''
    Настройка приложения

    :param app: приложение
    :type app: Application
    :return:
    :rtype: None
    '''

    setup_templates(app)
    setup_routes(app)


def run_mcp():
    mcp.run(transport='http', host='localhost', port=9000)


if __name__ == '__main__':
    thread_mcp = threading.Thread(target=run_mcp, daemon=True)
    thread_mcp.start()

    setup_app(application)
    web.run_app(application, port=settings.GENERAL.PORT)
