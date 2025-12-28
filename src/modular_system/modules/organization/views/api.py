from typing import Any
import json
class APIViews:
    def __init__(self, module):
        self.module = module
        self.logger = module.logger
    def list_api(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            org_service = self.module.env.get_service('organization_service')
            orgs = org_service.get_all() if org_service else []
            data = {
                'module': 'organization',
                'message': 'Organization list',
                'data': [org.to_dict() for org in orgs],
                'total': len(orgs)
            }
            response_body = json.dumps(data, indent=2).encode('utf-8')
            start_response('200 OK', [
                ('Content-Type', 'application/json'),
                ('Content-Length', str(len(response_body)))
            ])
            return [response_body]
        except Exception as e:
            self.logger.log("organization", f"Error in list API: {e}", "error")
            error_data = {'error': str(e)}
            error_body = json.dumps(error_data).encode('utf-8')
            start_response('500 Internal Server Error', [
                ('Content-Type', 'application/json'),
                ('Content-Length', str(len(error_body)))
            ])
            return [error_body]

    def create_api(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            from ..models.organization import OrganizationModel
            content_length = environ.get('CONTENT_LENGTH', '0')
            if not content_length or content_length == '0':
                error_data = {'error': 'Empty request body'}
                error_body = json.dumps(error_data).encode('utf-8')
                start_response('400 Bad Request', [
                    ('Content-Type', 'application/json'),
                    ('Content-Length', str(len(error_body)))
                ])
                return [error_body]
            
            request_body_size = int(content_length)
            request_body = environ['wsgi.input'].read(request_body_size)
            
            if not request_body:
                error_data = {'error': 'Empty request body'}
                error_body = json.dumps(error_data).encode('utf-8')
                start_response('400 Bad Request', [
                    ('Content-Type', 'application/json'),
                    ('Content-Length', str(len(error_body)))
                ])
                return [error_body]
            
            data = json.loads(request_body.decode('utf-8'))
            
            org_service = self.module.env.get_service('organization_service')
            
            existing_org = org_service.get_by_slug(data.get('slug'))
            if existing_org:
                error_data = {'error': f"Organization with slug '{data.get('slug')}' already exists"}
                error_body = json.dumps(error_data).encode('utf-8')
                start_response('409 Conflict', [
                    ('Content-Type', 'application/json'),
                    ('Content-Length', str(len(error_body)))
                ])
                return [error_body]
            
            new_org = OrganizationModel.from_dict(data)
            
            org_id = org_service.create(new_org)
            if org_id:
                response_data = {
                    'status': 'success',
                    'message': 'Organization created',
                    'id': org_id
                }
                status = '201 Created'
            else:
                response_data = {
                    'status': 'error',
                    'message': 'Failed to create organization'
                }
                status = '400 Bad Request'
                
            response_body = json.dumps(response_data, indent=2).encode('utf-8')
            start_response(status, [
                ('Content-Type', 'application/json'),
                ('Content-Length', str(len(response_body)))
            ])
            return [response_body]
        except json.JSONDecodeError as e:
            self.logger.log("organization", f"JSON decode error: {e}", "error")
            error_data = {'error': f'Invalid JSON: {str(e)}'}
            error_body = json.dumps(error_data).encode('utf-8')
            start_response('400 Bad Request', [
                ('Content-Type', 'application/json'),
                ('Content-Length', str(len(error_body)))
            ])
            return [error_body]
        except Exception as e:
            self.logger.log("organization", f"Error in create API: {e}", "error")
            error_data = {'error': str(e)}
            error_body = json.dumps(error_data).encode('utf-8')
            start_response('500 Internal Server Error', [
                ('Content-Type', 'application/json'),
                ('Content-Length', str(len(error_body)))
            ])
            return [error_body]
