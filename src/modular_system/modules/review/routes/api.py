def api_routes(module):
    routes = [
        ('/api/product/<id>/reviews', 'GET', module.api_views.product_reviews_api),
        ('/api/review/submit', 'POST', module.api_views.submit_review_api),
    ]
    return routes
