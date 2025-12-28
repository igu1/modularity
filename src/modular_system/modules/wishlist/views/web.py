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
            user_id = 1
            wishlist_service = self.module.env.get_service('wishlist_service')
            wishlist_items = wishlist_service.get_user_wishlist(org.id, user_id)
            product_service = self.module.env.get_service('product_service')
            items_html = []
            for item in wishlist_items:
                product = product_service.get_by_id(item.product_id)
                if product:
                    items_html.append(f"""
                        <div class="wishlist-item">
                            <span>{product.name}</span>
                            <span>${product.price/100:.2f}</span>
                            <div>
                                <a href="/cart/add/{product.id}" class="add-to-cart">Add to Cart</a>
                                <a href="/wishlist/remove/{item.id}" class="remove-btn">Remove</a>
                            </div>
                        </div>
                    """)
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>My Wishlist - {org.name}</title>
    <style>
        body {{ font-family: sans-serif; margin: 20px; background: #f0f2f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
        .wishlist-item {{ display: flex; justify-content: space-between; align-items: center; padding: 15px 0; border-bottom: 1px solid #ddd; }}
        .add-to-cart {{ padding: 5px 10px; background: #ffd814; text-decoration: none; color: black; border-radius: 4px; font-size: 0.9em; }}
        .remove-btn {{ color: #c40000; text-decoration: none; font-size: 0.9em; margin-left: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>My Wishlist - {org.name}</h1>
        {"".join(items_html) if items_html else "<p>Your wishlist is empty</p>"}
        <p><a href="/product">Continue Shopping</a></p>
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
            self.logger.log("wishlist", f"Error in list view: {e}", "error")
            error_body = f"Error: {str(e)}".encode('utf-8')
            start_response('500 Internal Server Error', [
                ('Content-Type', 'text/plain'),
                ('Content-Length', str(len(error_body)))
            ])
            return [error_body]
    def add_to_wishlist_view(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            org = environ.get('ORG_CONTEXT')
            params = environ.get('ROUTE_PARAMS', {})
            product_id = int(params.get('product_id'))
            user_id = 1
            wishlist_service = self.module.env.get_service('wishlist_service')
            from ..models.wishlist import WishlistModel
            new_item = WishlistModel(organization_id=org.id, user_id=user_id, product_id=product_id)
            wishlist_service.create(new_item)
            start_response('302 Found', [('Location', '/wishlist')])
            return [b""]
        except Exception as e:
            self.logger.log("wishlist", f"Error adding to wishlist: {e}", "error")
            start_response('500 Internal Server Error', [('Content-Type', 'text/plain')])
            return [str(e).encode('utf-8')]
    def remove_from_wishlist_view(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            params = environ.get('ROUTE_PARAMS', {})
            item_id = int(params.get('item_id'))
            wishlist_service = self.module.env.get_service('wishlist_service')
            wishlist_service.delete(item_id)
            start_response('302 Found', [('Location', '/wishlist')])
            return [b""]
        except Exception as e:
            self.logger.log("wishlist", f"Error removing from wishlist: {e}", "error")
            start_response('500 Internal Server Error', [('Content-Type', 'text/plain')])
            return [str(e).encode('utf-8')]
