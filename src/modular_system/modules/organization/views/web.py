from typing import Any
class WebViews:
    def __init__(self, module):
        self.module = module
        self.logger = module.logger
    def list_view(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            org_service = self.module.env.get_service('organization_service')
            orgs = org_service.get_all() if org_service else []
            orgs_html = "".join([f'<li>{org.name} ({org.slug})</li>' for org in orgs])
            html = f"<html><body><h1>Organizations</h1><ul>{orgs_html}</ul></body></html>"
            response_body = html.encode('utf-8')
            start_response('200 OK', [
                ('Content-Type', 'text/html'),
                ('Content-Length', str(len(response_body)))
            ])
            return [response_body]
        except Exception as e:
            self.logger.log("organization", f"Error in list view: {e}", "error")
            error_body = f"Error: {str(e)}".encode('utf-8')
            start_response('500 Internal Server Error', [
                ('Content-Type', 'text/plain'),
                ('Content-Length', str(len(error_body)))
            ])
            return [error_body]
    def create_view(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            html = "<html><body><h1>Create Organization</h1><p>Use the API to create organizations.</p></body></html>"
            response_body = html.encode('utf-8')
            start_response('200 OK', [
                ('Content-Type', 'text/html'),
                ('Content-Length', str(len(response_body)))
            ])
            return [response_body]
        except Exception as e:
            self.logger.log("organization", f"Error in create view: {e}", "error")
            error_body = f"Error: {str(e)}".encode('utf-8')
            start_response('500 Internal Server Error', [
                ('Content-Type', 'text/plain'),
                ('Content-Length', str(len(error_body)))
            ])
            return [error_body]
