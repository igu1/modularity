def api_routes(module):
    routes = [
        ('/api/product/<id>/recommendations', 'GET', module.api_views.recommendations_api),
        ('/api/recommendation/add', 'POST', module.api_views.add_recommendation_api),
    ]
    return routes
