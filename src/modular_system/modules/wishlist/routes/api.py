def get_routes(module):
    routes = [
        ('/wishlist', 'GET', module.web_views.list_view),
        ('/wishlist/create', 'GET', module.web_views.create_view),
        ('/wishlist/create', 'POST', module.web_views.create_view),
        ('/api/wishlist', 'GET', module.api_views.list_api),
    ]
    return routes
