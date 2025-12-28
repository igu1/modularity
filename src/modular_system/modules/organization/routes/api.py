def get_routes(module):
    routes = [
        ('/organization', 'GET', module.web_views.list_view),
        ('/organization/create', 'GET', module.web_views.create_view),
        ('/organization/create', 'POST', module.web_views.create_view),
        ('/api/organization', 'GET', module.api_views.list_api),
        ('/api/organization', 'POST', module.api_views.create_api),
    ]
    return routes
