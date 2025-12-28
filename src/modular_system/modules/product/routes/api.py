def get_routes(module):
    routes = [
        ('/product', 'GET', module.web_views.list_view),
        ('/product/create', 'GET', module.web_views.create_view),
        ('/product/create', 'POST', module.web_views.create_view),
        ('/api/product', 'GET', module.api_views.list_api),
    ]
    return routes
