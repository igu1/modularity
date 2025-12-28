def get_routes(module):
    routes = [
        ('/cart', 'GET', module.web_views.list_view),
        ('/cart/add/<product_id>', 'GET', module.web_views.add_to_cart_view),
        ('/cart/remove/<item_id>', 'GET', module.web_views.remove_from_cart_view),
        ('/api/cart', 'GET', module.api_views.list_api),
    ]
    return routes
