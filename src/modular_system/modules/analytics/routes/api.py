def api_routes(module):
    routes = [
        ('/api/analytics/track', 'POST', module.api_views.track_api),
        ('/api/analytics/stats', 'GET', module.api_views.stats_api),
    ]
    return routes
