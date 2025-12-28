def get_routes(module):
    views = module.api_views
    routes = [
        ('/api/products', 'GET', views.list_api),
        ('/api/products', 'POST', views.create_api),
        ('/api/products/<id>', 'GET', views.get_api),
        ('/api/products/<id>', 'PUT', views.update_api),
        ('/api/products/<id>', 'DELETE', views.delete_api),
    ]
    return routes
