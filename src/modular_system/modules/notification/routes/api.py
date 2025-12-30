def api_routes(module):
    routes = [
        ('/api/notifications/<user_id>', 'GET', module.api_views.user_notifications_api),
        ('/api/notifications/read', 'POST', module.api_views.mark_read_api),
    ]
    return routes
