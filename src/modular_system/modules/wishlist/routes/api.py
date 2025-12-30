def api_routes(module):
    routes = [
        ('/api/wishlist/<user_id>', 'GET', module.api_views.user_wishlist_api),
        ('/api/wishlist/add', 'POST', module.api_views.add_to_wishlist_api),
    ]
    return routes
