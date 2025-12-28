def get_routes(module):
    routes = [
        ('/cart', 'GET', module.web_views.list_view),
        ('/cart/create', 'GET', module.web_views.create_view),
        ('/cart/create', 'POST', module.web_views.create_view),
        ('/api/cart', 'GET', module.api_views.list_api),
    ]
    return routes
