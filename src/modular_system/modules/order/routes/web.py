def get_routes(module):
    routes = [
        ('/order/success', 'GET', module.web_views.order_success_view),
        ('/orders', 'GET', module.web_views.list_view),
        ('/order/<order_id>', 'GET', module.web_views.detail_view),
        ('/api/order', 'GET', module.api_views.list_api),
    ]
    return routes
