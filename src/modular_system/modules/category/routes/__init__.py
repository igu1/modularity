def get_routes(module):
    return [
        ('/api/category', 'GET', module.api_views.list_api),
        ('/api/category/create', 'POST', module.api_views.create_api)
    ]
