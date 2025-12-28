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
            order_service = self.module.env.get_service('order_service')
            orders = order_service.get_user_orders(org.id, user_id)
            orders_html = []
            for order in orders:
                orders_html.append(f"""
                    <div class="order-card">
                        <div class="order-header">
                            <span>Order #{order.id}</span>
                            <span>{order.created_at}</span>
                        </div>
                        <div class="order-body">
                            <p>Status: <span class="status-{order.status}">{order.status}</span></p>
                            <p>Total: ${order.total_amount/100:.2f}</p>
                            <a href="/order/{order.id}" class="btn-detail">View Details</a>
                        </div>
                    </div>
                """)
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>My Orders - {org.name}</title>
    <style>
        body {{ font-family: sans-serif; margin: 20px; background: #f0f2f5; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        .order-card {{ background: white; padding: 15px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .order-header {{ display: flex; justify-content: space-between; border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 10px; font-weight: bold; }}
        .status-pending {{ color: #ffa500; }}
        .status-completed {{ color: #008000; }}
        .btn-detail {{ display: inline-block; margin-top: 10px; padding: 5px 10px; border: 1px solid #ccc; border-radius: 4px; text-decoration: none; color: #333; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>My Orders - {org.name}</h1>
        {"".join(orders_html) if orders_html else "<p>You have no orders yet.</p>"}
        <p><a href="/product">Back to Products</a></p>
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
            self.logger.log("order", f"Error in list view: {e}", "error")
            start_response('500 Internal Server Error', [('Content-Type', 'text/plain')])
            return [str(e).encode('utf-8')]
    def order_success_view(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            org = environ.get('ORG_CONTEXT')
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Order Successful - {org.name if org else 'E-commerce'}</title>
    <style>
        body {{ font-family: sans-serif; margin: 20px; text-align: center; padding-top: 50px; }}
        .success-icon {{ font-size: 50px; color: #4CAF50; }}
        .btn {{ display: inline-block; padding: 10px 20px; background: #ffd814; text-decoration: none; color: black; border-radius: 8px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="success-icon">✓</div>
    <h1>Thank you for your order!</h1>
    <p>Your order has been placed successfully.</p>
    <a href="/orders" class="btn">View My Orders</a>
    <br>
    <a href="/product" style="display:inline-block; margin-top: 10px; color: #0066c0;">Continue Shopping</a>
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
            start_response('500 Internal Server Error', [('Content-Type', 'text/plain')])
            return [str(e).encode('utf-8')]
    def detail_view(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            params = environ.get('ROUTE_PARAMS', {})
            order_id = int(params.get('order_id'))
            order_service = self.module.env.get_service('order_service')
            order = order_service.get_by_id(order_id)
            if not order:
                start_response('404 Not Found', [('Content-Type', 'text/plain')])
                return [b"Order not found"]
            html = f"<h1>Order #{order.id}</h1><p>Status: {order.status}</p><p>Total: ${order.total_amount/100:.2f}</p><p>Shipping to: {order.shipping_address}</p><a href='/orders'>Back to Orders</a>"
            response_body = html.encode('utf-8')
            start_response('200 OK', [
                ('Content-Type', 'text/html'),
                ('Content-Length', str(len(response_body)))
            ])
            return [response_body]
        except Exception as e:
            start_response('500 Internal Server Error', [('Content-Type', 'text/plain')])
            return [str(e).encode('utf-8')]
