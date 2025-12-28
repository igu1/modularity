def get_routes(module):
    routes = [
        ('/order', 'GET', module.web_views.list_view),
        ('/order/create', 'GET', module.web_views.create_view),
        ('/order/create', 'POST', module.web_views.create_view),
        ('/api/order', 'GET', module.api_views.list_api),
    ]
    return routes
