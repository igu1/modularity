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
            cart_service = self.module.env.get_service('cart_service')
            cart_items = cart_service.get_user_cart(org.id, user_id)
            product_service = self.module.env.get_service('product_service')
            total = 0
            items_html = []
            for item in cart_items:
                product = product_service.get_by_id(item.product_id)
                if product:
                    subtotal = product.price * item.quantity
                    total += subtotal
                    items_html.append(f"""
                        <div class="cart-item">
                            <span>{product.name} (x{item.quantity})</span>
                            <span>${subtotal/100:.2f}</span>
                            <a href="/cart/remove/{item.id}" class="remove-btn">Remove</a>
                        </div>
                    """)
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Shopping Cart - {org.name}</title>
    <style>
        body {{ font-family: sans-serif; margin: 20px; background: #f0f2f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
        .cart-item {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #ddd; }}
        .total {{ font-size: 1.5em; font-weight: bold; text-align: right; margin-top: 20px; }}
        .checkout-btn {{ display: block; width: 200px; margin: 20px 0 0 auto; padding: 10px; background: #ffd814; text-align: center; text-decoration: none; color: black; border-radius: 8px; }}
        .remove-btn {{ color: #c40000; text-decoration: none; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Your Cart - {org.name}</h1>
        {"".join(items_html) if items_html else "<p>Your cart is empty</p>"}
        {f'<div class="total">Total: ${total/100:.2f}</div><a href="/checkout" class="checkout-btn">Proceed to Checkout</a>' if items_html else ''}
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
            self.logger.log("cart", f"Error in list view: {e}", "error")
            error_body = f"Error: {str(e)}".encode('utf-8')
            start_response('500 Internal Server Error', [
                ('Content-Type', 'text/plain'),
                ('Content-Length', str(len(error_body)))
            ])
            return [error_body]
    def add_to_cart_view(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            org = environ.get('ORG_CONTEXT')
            params = environ.get('ROUTE_PARAMS', {})
            product_id = int(params.get('product_id'))
            user_id = 1
            cart_service = self.module.env.get_service('cart_service')
            from ..models.cart import CartModel
            new_item = CartModel(organization_id=org.id, user_id=user_id, product_id=product_id, quantity=1)
            cart_service.create(new_item)
            start_response('302 Found', [('Location', '/cart')])
            return [b""]
        except Exception as e:
            self.logger.log("cart", f"Error adding to cart: {e}", "error")
            start_response('500 Internal Server Error', [('Content-Type', 'text/plain')])
            return [str(e).encode('utf-8')]
    def remove_from_cart_view(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            params = environ.get('ROUTE_PARAMS', {})
            item_id = int(params.get('item_id'))
            cart_service = self.module.env.get_service('cart_service')
            cart_service.delete(item_id)
            start_response('302 Found', [('Location', '/cart')])
            return [b""]
        except Exception as e:
            self.logger.log("cart", f"Error removing from cart: {e}", "error")
            start_response('500 Internal Server Error', [('Content-Type', 'text/plain')])
            return [str(e).encode('utf-8')]
