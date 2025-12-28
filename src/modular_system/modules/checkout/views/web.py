from typing import Any
class WebViews:
    def __init__(self, module):
        self.module = module
        self.logger = module.logger
    def checkout_view(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            org = environ.get('ORG_CONTEXT')
            if not org:
                start_response('404 Not Found', [('Content-Type', 'text/plain')])
                return [b"Organization not found"]
            user_id = 1
            cart_service = self.module.env.get_service('cart_service')
            cart_items = cart_service.get_user_cart(org.id, user_id)
            if not cart_items:
                start_response('302 Found', [('Location', '/cart')])
                return [b""]
            product_service = self.module.env.get_service('product_service')
            total = 0
            for item in cart_items:
                product = product_service.get_by_id(item.product_id)
                if product:
                    total += product.price * item.quantity
            checkout_service = self.module.env.get_service('checkout_service')
            session_id = checkout_service.create_session(org.id, user_id)
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Checkout - {org.name}</title>
    <style>
        body {{ font-family: sans-serif; margin: 20px; background: #f0f2f5; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
        .form-group {{ margin-bottom: 15px; }}
        label {{ display: block; margin-bottom: 5px; }}
        textarea {{ width: 100%; height: 100px; }}
        .btn {{ display: block; width: 100%; padding: 10px; background: #ffd814; text-align: center; border: none; border-radius: 8px; cursor: pointer; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Checkout - {org.name}</h1>
        <p>Total Amount: ${total/100:.2f}</p>
        <form action="/checkout/complete" method="POST">
            <input type="hidden" name="session_id" value="{session_id}">
            <div class="form-group">
                <label>Shipping Address</label>
                <textarea name="shipping_address" required placeholder="Enter your full address..."></textarea>
            </div>
            <button type="submit" class="btn">Place Order</button>
        </form>
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
            self.logger.log("checkout", f"Error in checkout view: {e}", "error")
            start_response('500 Internal Server Error', [('Content-Type', 'text/plain')])
            return [str(e).encode('utf-8')]
    def complete_checkout_view(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            import urllib.parse
            content_length = int(environ.get('CONTENT_LENGTH', 0))
            post_data = environ['wsgi.input'].read(content_length).decode('utf-8')
            params = urllib.parse.parse_qs(post_data)
            session_id = int(params.get('session_id', [0])[0])
            shipping_address = params.get('shipping_address', [''])[0]
            checkout_service = self.module.env.get_service('checkout_service')
            success = checkout_service.complete_checkout(session_id, shipping_address)
            if success:
                start_response('302 Found', [('Location', '/order/success')])
                return [b""]
            else:
                start_response('500 Internal Server Error', [('Content-Type', 'text/plain')])
                return [b"Failed to complete checkout"]
        except Exception as e:
            self.logger.log("checkout", f"Error completing checkout: {e}", "error")
            start_response('500 Internal Server Error', [('Content-Type', 'text/plain')])
            return [str(e).encode('utf-8')]
