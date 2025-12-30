def api_routes(mod):
    v = mod.api_views
    return [
        ('/api/health', 'GET', v.health_api), ('/api/status', 'GET', v.status_api),
        ('/api/auth/register', 'POST', v.register_api), ('/api/auth/login', 'POST', v.login_api),
        ('/api/auth/refresh', 'POST', v.refresh_token_api),
        ('/api/organizations', 'GET', v.organization_list), ('/api/organizations', 'POST', v.organization_create),
        ('/api/organizations/<id>', 'GET', v.organization_get), ('/api/organizations/<id>', 'PUT', v.organization_update),
        ('/api/organizations/<id>', 'DELETE', v.organization_delete)
    ]
