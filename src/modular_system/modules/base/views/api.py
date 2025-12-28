import json
from ..models.organization import OrganizationModel

class APIViews:
    def __init__(self, mod): self.mod = mod

    def _resp(self, data, start, status='200 OK'):
        body = json.dumps(data).encode()
        start(status, [('Content-Type', 'application/json'), ('Content-Length', str(len(body)))])
        return [body]

    def _err(self, msg, start, status='500 Error'): return self._resp({"success": False, "error": msg}, start, status)

    def organization_list(self, env, start, mod):
        return self._resp([o.to_dict() for o in self.mod.services['organization_service'].get_all()], start)

    def organization_get(self, env, start, mod):
        oid = int(env.get('ROUTE_PARAMS', {}).get('id', 0))
        o = self.mod.services['organization_service'].get_by_id(oid)
        return self._resp(o.to_dict(), start) if o else self._err("Not found", start, '404 Not Found')

    def organization_create(self, env, start, mod):
        data = json.loads(env['wsgi.input'].read(int(env.get('CONTENT_LENGTH', 0))))
        oid = self.mod.services['organization_service'].create(OrganizationModel.from_dict(data))
        return self._resp({"id": oid}, start, '201 Created') if oid else self._err("Fail", start)

    def organization_update(self, env, start, mod):
        oid = int(env.get('ROUTE_PARAMS', {}).get('id', 0))
        data = json.loads(env['wsgi.input'].read(int(env.get('CONTENT_LENGTH', 0))))
        return self._resp({"msg": "OK"}, start) if self.mod.services['organization_service'].update(oid, OrganizationModel.from_dict(data)) else self._err("Fail", start)

    def organization_delete(self, env, start, mod):
        oid = int(env.get('ROUTE_PARAMS', {}).get('id', 0))
        return self._resp({"msg": "OK"}, start) if self.mod.services['organization_service'].delete(oid) else self._err("Fail", start)

    def health_api(self, env, start, mod):
        return self._resp({"status": "healthy", "ts": str(datetime.now())}, start)

    def status_api(self, env, start, mod):
        return self._resp({"system": self.mod.get_system_status()}, start)
