def api_routes(module):
    routes = [
        ('/api/support/tickets/<user_id>', 'GET', module.api_views.user_tickets_api),
        ('/api/support/tickets/create', 'POST', module.api_views.create_ticket_api),
    ]
    return routes
