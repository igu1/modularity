def get_routes(module):
    routes = [
        ('/category', 'GET', module.web_views.list_view),
        ('/category/create', 'GET', module.web_views.create_view),
        ('/category/create', 'POST', module.web_views.create_view),
        ('/api/category', 'GET', module.api_views.list_api),
    ]
    return routes
