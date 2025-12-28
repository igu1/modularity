from typing import Any
class WebViews:
    def __init__(self, module):
        self.module = module
        self.logger = module.logger
    def home_view(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            org_service = self.module.env.get_service('organization_service')
            orgs = org_service.get_all() if org_service else []
            orgs_html = []
            for org in orgs:
                orgs_html.append(f'<li><a href="http://{org.slug}.localhost:8080/product">{org.name}</a> ({org.description})</li>')
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Modular SaaS E-commerce</title>
    <style>
        body {{ font-family: sans-serif; margin: 40px; line-height: 1.6; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        h1 {{ color: #333; }}
        .org-list {{ margin-top: 20px; }}
        .admin-link {{ display: inline-block; margin-top: 30px; color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Modular SaaS E-commerce Platform</h1>
        <p>Welcome to the multi-tenant e-commerce platform. Select an organization to start shopping:</p>
        <ul class="org-list">
            {"".join(orgs_html) if orgs_html else "<li>No organizations registered yet.</li>"}
        </ul>
        <hr>
        <p>To register a new organization or manage the system, please use the CLI or API.</p>
    </div>
</body>
</html>
"""
            response_body = html.encode('utf-8')
            start_response('200 OK', [
                ('Content-Type', 'text/html'),
                ('Content-Length', str(len(response_body)))
            ])
            return [response_body]
        except Exception as e:
            self.logger.log("base", f"Error in home view: {e}", "error")
            error_body = f"Error: {str(e)}".encode('utf-8')
            start_response('500 Internal Server Error', [
                ('Content-Type', 'text/plain'),
                ('Content-Length', str(len(error_body)))
            ])
            return [error_body]
    def health_view(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            db_status = "Connected"
            try:
                from modular_system.database.connection import get_engine
                engine = get_engine()
                with engine.connect() as conn:
                    from sqlalchemy import text
                    conn.execute(text("SELECT 1"))
            except Exception:
                db_status = "Disconnected"
            html = f"""
<!DOCTYPE html>
<html>
<head><title>System Health</title></head>
<body><h1>System Health</h1><p>Database: {db_status}</p></body>
</html>
"""
            response_body = html.encode('utf-8')
            start_response('200 OK', [
                ('Content-Type', 'text/html'),
                ('Content-Length', str(len(response_body)))
            ])
            return [response_body]
        except Exception as e:
            self.logger.log("base", f"Error in health view: {e}", "error")
            error_body = f"Error: {str(e)}".encode('utf-8')
            start_response('500 Internal Server Error', [
                ('Content-Type', 'text/plain'),
                ('Content-Length', str(len(error_body)))
            ])
            return [error_body]
