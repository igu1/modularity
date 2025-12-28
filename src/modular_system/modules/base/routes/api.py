def api_routes(module):
    views = module.api_views
    return [
        ('/api/health', 'GET', views.health_api),
        ('/api/status', 'GET', views.status_api),
        ('/api/organizations', 'GET', views.organization_list),
        ('/api/organizations', 'POST', views.organization_create),
        ('/api/organizations/<id>', 'GET', views.organization_get),
        ('/api/organizations/<id>', 'PUT', views.organization_update),
        ('/api/organizations/<id>', 'DELETE', views.organization_delete),
    ]
