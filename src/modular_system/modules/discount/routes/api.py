def api_routes(module):
    routes = [
        ('/api/discount', 'GET', module.api_views.list_api),
        ('/api/discount/validate', 'POST', module.api_views.validate_coupon_api),
    ]
    return routes
