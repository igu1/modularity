def get_routes(module):
    routes = [
        ('/checkout', 'GET', module.web_views.list_view),
        ('/checkout/create', 'GET', module.web_views.create_view),
        ('/checkout/create', 'POST', module.web_views.create_view),
        ('/api/checkout', 'GET', module.api_views.list_api),
    ]
    return routes
