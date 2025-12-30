def get_routes(module):
    return [
        ('/api/cart', 'GET', module.api_views.list_api),
        ('/api/cart/create', 'POST', module.api_views.create_api)
    ]
