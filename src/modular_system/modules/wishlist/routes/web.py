def get_routes(module):
    routes = [
        ('/wishlist', 'GET', module.web_views.list_view),
        ('/wishlist/add/<product_id>', 'GET', module.web_views.add_to_wishlist_view),
        ('/wishlist/remove/<item_id>', 'GET', module.web_views.remove_from_wishlist_view),
        ('/api/wishlist', 'GET', module.api_views.list_api),
    ]
    return routes
