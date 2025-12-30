import json
from modular_system.extensions.patch_types import Patch, RoutePatch
from modular_system.database.connection import get_engine
from sqlalchemy import text

class VariantPatch(Patch):
    def __init__(self):
        super().__init__("product_variant_patch", "Adds variant support (Size, Color, etc.) to products")
        self.target = "product"

    def apply(self, inst, env):
        self._create_tables()
        inst.logger.log("product", "Applied Variant Patch: Table created", "info")

    def _create_tables(self):
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS product_variants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    attribute_name VARCHAR(100) NOT NULL,
                    attribute_value VARCHAR(255) NOT NULL,
                    price_extra DECIMAL(10, 2) DEFAULT 0,
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            """))
            conn.commit()

def list_variants_api(environ, start_response, env):
    params = environ.get('ROUTE_PARAMS', {})
    product_id = params.get('id')
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM product_variants WHERE product_id = :id"), {"id": product_id}).fetchall()
        data = {
            "success": True,
            "product_id": product_id,
            "variants": [dict(id=r[0], name=r[2], value=r[3], extra=float(r[4])) for r in result]
        }
        body = json.dumps(data).encode('utf-8')
        start_response('200 OK', [('Content-Type', 'application/json'), ('Content-Length', str(len(body)))])
        return [body]

def create_variant_api(environ, start_response, env):
    try:
        content_length = int(environ.get('CONTENT_LENGTH', 0))
        data = json.loads(environ['wsgi.input'].read(content_length))
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("""
                INSERT INTO product_variants (product_id, attribute_name, attribute_value, price_extra)
                VALUES (:product_id, :name, :value, :extra)
                RETURNING id
            """), {
                "product_id": data.get('product_id'),
                "name": data.get('attribute_name'),
                "value": data.get('attribute_value'),
                "extra": data.get('price_extra', 0)
            })
            new_id = result.fetchone()[0]
            conn.commit()
        body = json.dumps({"success": True, "id": new_id}).encode('utf-8')
        start_response('201 Created', [('Content-Type', 'application/json'), ('Content-Length', str(len(body)))])
        return [body]
    except Exception as e:
        body = json.dumps({"success": False, "error": str(e)}).encode('utf-8')
        start_response('500 Internal Server Error', [('Content-Type', 'application/json'), ('Content-Length', str(len(body)))])
        return [body]

def get_patches():
    return [
        VariantPatch(),
        RoutePatch("product_variant_list_route", "/api/product/<id>/variants", "GET", list_variants_api, "product"),
        RoutePatch("product_variant_create_route", "/api/product/variants", "POST", create_variant_api, "product")
    ]
