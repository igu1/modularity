def get_routes(module):
    routes = [
        ('/checkout', 'GET', module.web_views.checkout_view),
        ('/checkout/complete', 'POST', module.web_views.complete_checkout_view),
        ('/api/checkout', 'GET', module.api_views.list_api),
    ]
    return routes
