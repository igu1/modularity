def api_routes(module):
    routes = [
        ('/api/subscriptions/<user_id>', 'GET', module.api_views.user_subscriptions_api),
        ('/api/subscriptions/create', 'POST', module.api_views.create_subscription_api),
    ]
    return routes
