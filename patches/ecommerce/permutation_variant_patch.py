import json
from modular_system.extensions.patch_types import Patch, RoutePatch
from modular_system.database.connection import get_engine
from sqlalchemy import text

class PermutationVariantPatch(Patch):
    def __init__(self):
        super().__init__("product_permutation_variant_patch", "Adds complex permutation variant support (SKUs, Stock) to products")
        self.target = "product"

    def apply(self, inst, env):
        self._create_tables()
        inst.logger.log("product", "Applied Permutation Variant Patch: Table created", "info")

    def _create_tables(self):
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS product_permutations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    sku VARCHAR(100) UNIQUE,
                    attributes JSON NOT NULL,
                    price DECIMAL(10, 2),
                    stock INTEGER DEFAULT 0,
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            """))
            conn.commit()

def list_permutations_api(environ, start_response, env):
    params = environ.get('ROUTE_PARAMS', {})
    product_id = params.get('id')
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM product_permutations WHERE product_id = :id"), {"id": product_id}).fetchall()
        data = {
            "success": True,
            "product_id": product_id,
            "permutations": [dict(id=r[0], sku=r[2], attributes=json.loads(r[3]) if isinstance(r[3], str) else r[3], price=float(r[4]), stock=r[5]) for r in result]
        }
        body = json.dumps(data).encode('utf-8')
        start_response('200 OK', [('Content-Type', 'application/json'), ('Content-Length', str(len(body)))])
        return [body]

def create_permutation_api(environ, start_response, env):
    try:
        content_length = int(environ.get('CONTENT_LENGTH', 0))
        data = json.loads(environ['wsgi.input'].read(content_length))
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("""
                INSERT INTO product_permutations (product_id, sku, attributes, price, stock)
                VALUES (:product_id, :sku, :attributes, :price, :stock)
                RETURNING id
            """), {
                "product_id": data.get('product_id'),
                "sku": data.get('sku'),
                "attributes": json.dumps(data.get('attributes', {})),
                "price": data.get('price'),
                "stock": data.get('stock', 0)
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
        PermutationVariantPatch(),
        RoutePatch("product_permutation_list_route", "/api/product/<id>/variants/permutation", "GET", list_permutations_api, "product"),
        RoutePatch("product_permutation_create_route", "/api/product/variants/permutation", "POST", create_permutation_api, "product")
    ]
