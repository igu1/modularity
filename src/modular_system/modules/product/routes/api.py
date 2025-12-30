def api_routes(module):
    routes = [
        ('/api/product', 'GET', module.api_views.list_api),
        ('/api/product/create', 'POST', module.api_views.create_api),
    ]
    return routes
