def web_routes(module):
    routes = [
        ('/web/product', 'GET', module.web_views.list_view),
        ('/web/product/create', 'GET', module.web_views.create_view),
        ('/web/product/create', 'POST', module.web_views.create_view),
    ]
    return routes
