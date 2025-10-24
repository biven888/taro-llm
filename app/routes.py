from app import views


def setup_routes(app: views.web.Application):
    '''
    Добавление путей к router приложения

    :param app: приложение, для которого добавляются пути
    :type app: Application
    :return:
    '''

    app.router.add_get('/', views.index)
    app.router.add_get('/ws', views.websocket_handler)
