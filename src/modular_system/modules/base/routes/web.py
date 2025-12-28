def web_routes(mod):
    v = mod.web_views
    return [('/', 'GET', v.home_view), ('/health', 'GET', v.health_view), ('/status', 'GET', v.health_view)]
