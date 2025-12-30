def api_routes(module):
    routes = [
        ('/api/segmentation', 'GET', module.api_views.list_api),
        ('/api/segmentation/assign', 'POST', module.api_views.assign_api),
    ]
    return routes
