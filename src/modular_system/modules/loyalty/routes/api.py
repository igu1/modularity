def api_routes(module):
    routes = [
        ('/api/loyalty/points/<user_id>', 'GET', module.api_views.get_points_api),
        ('/api/loyalty/add', 'POST', module.api_views.add_points_api),
    ]
    return routes
