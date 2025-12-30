def api_routes(module):
    routes = [
        ('/api/inventory/alerts', 'GET', module.api_views.alerts_api),
        ('/api/inventory/threshold', 'POST', module.api_views.set_threshold_api),
    ]
    return routes
