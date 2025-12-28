from typing import Any
class WebViews:
    def __init__(self, module):
        self.module = module
        self.logger = module.logger
    def list_view(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            org = environ.get('ORG_CONTEXT')
            if not org:
                start_response('404 Not Found', [('Content-Type', 'text/plain')])
                return [b"Organization not found"]
            
            import urllib.parse
            query_params = urllib.parse.parse_qs(environ.get('QUERY_STRING', ''))
            category_id = query_params.get('category', [None])[0]
            if category_id: category_id = int(category_id)
            
            product_service = self.module.env.get_service('product_service')
            products = product_service.get_all(organization_id=org.id, category_id=category_id)
            
            category_service = self.module.env.get_service('category_service')
            categories = category_service.get_all(organization_id=org.id)
            
            cat_links = [f'<li><a href="/product">All</a></li>']
            for cat in categories:
                cat_links.append(f'<li><a href="/product?category={cat.id}">{cat.name}</a></li>')
            
            products_html = []
            for p in products:
                products_html.append(f'''
                    <div class="product-card">
                        <h3>{p.name}</h3>
                        <p>{p.description}</p>
                        <p class="price">${p.price/100:.2f}</p>
                        <a href="/cart/add/{p.id}" class="btn">Add to Cart</a>
                        <a href="/wishlist/add/{p.id}" class="btn wishlist-btn">Wishlist</a>
                    </div>
                ''')
            
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{org.name} - Products</title>
    <style>
        body {{ font-family: sans-serif; margin: 0; background: #f0f2f5; display: flex; }}
        .sidebar {{ width: 200px; background: white; padding: 20px; border-right: 1px solid #ddd; height: 100vh; }}
        .content {{ flex: 1; padding: 20px; }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        .product-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; }}
        .product-card {{ background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .price {{ color: #b12704; font-size: 1.2em; font-weight: bold; }}
        .btn {{ display: inline-block; padding: 8px 15px; background: #ffd814; border: 1px solid #fcd200; border-radius: 20px; text-decoration: none; color: black; margin-top: 10px; font-size: 0.9em; }}
        .wishlist-btn {{ background: #f0f2f5; border: 1px solid #adb1b8; }}
        .nav-links {{ margin-bottom: 20px; }}
        .nav-links a {{ margin-right: 15px; text-decoration: none; color: #0066c0; }}
    </style>
</head>
<body>
    <div class="sidebar">
        <h3>Categories</h3>
        <ul>{"".join(cat_links)}</ul>
    </div>
    <div class="content">
        <div class="container">
            <div class="nav-links">
                <a href="/cart">View Cart</a>
                <a href="/wishlist">My Wishlist</a>
                <a href="/orders">My Orders</a>
            </div>
            <h1>Welcome to {org.name}</h1>
            <div class="product-grid">
                {"".join(products_html) if products_html else "<p>No products found.</p>"}
            </div>
        </div>
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
            self.logger.log("product", f"Error in list view: {e}", "error")
            error_body = f"Error: {str(e)}".encode('utf-8')
            start_response('500 Internal Server Error', [
                ('Content-Type', 'text/plain'),
                ('Content-Length', str(len(error_body)))
            ])
            return [error_body]
    def create_view(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            html = "<html><body><h1>Create Product</h1><p>Use the API to manage products.</p></body></html>"
            response_body = html.encode('utf-8')
            start_response('200 OK', [
                ('Content-Type', 'text/html'),
                ('Content-Length', str(len(response_body)))
            ])
            return [response_body]
        except Exception as e:
            self.logger.log("product", f"Error in create view: {e}", "error")
            error_body = f"Error: {str(e)}".encode('utf-8')
            start_response('500 Internal Server Error', [
                ('Content-Type', 'text/plain'),
                ('Content-Length', str(len(error_body)))
            ])
            return [error_body]
