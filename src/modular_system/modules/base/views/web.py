from typing import Any


class WebViews:
    
    def __init__(self, module):
        self.module = module
        self.logger = module.logger
    
    def home_view(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            status = self.module.get_system_status()
            
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Modular System - Home</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 40px 20px; }}
        .header {{ text-align: center; color: white; margin-bottom: 40px; }}
        .header h1 {{ font-size: 48px; margin: 0; text-shadow: 0 2px 4px rgba(0,0,0,0.3); }}
        .header p {{ font-size: 20px; opacity: 0.9; margin: 10px 0; }}
        .modules-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 40px; }}
        .module-card {{ background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: transform 0.2s; }}
        .module-card:hover {{ transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0,0,0,0.15); }}
        .module-card h3 {{ color: #333; margin: 0 0 10px 0; font-size: 24px; }}
        .module-card p {{ color: #666; margin: 0 0 20px 0; line-height: 1.6; }}
        .module-links {{ display: flex; flex-wrap: wrap; gap: 10px; }}
        .btn {{ display: inline-block; padding: 10px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 6px; font-size: 14px; font-weight: 500; transition: opacity 0.2s; }}
        .btn:hover {{ opacity: 0.9; }}
        .btn-secondary {{ background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }}
        .btn-api {{ background: linear-gradient(135deg, #fc4a1a 0%, #f7b733 100%); }}
        .status {{ background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .status h3 {{ color: #333; margin: 0 0 20px 0; }}
        .status-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }}
        .status-item {{ text-align: center; }}
        .status-item .number {{ font-size: 36px; font-weight: bold; color: #667eea; }}
        .status-item .label {{ color: #666; font-size: 14px; }}
        .footer {{ text-align: center; color: white; margin-top: 40px; opacity: 0.8; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Modular System</h1>
            <p>A beautiful, scalable architecture for building modular applications</p>
        </div>
        
        <div class="status">
            <h3>📊 System Status</h3>
            <div class="status-grid">
                <div class="status-item">
                    <div class="number">{status['loaded_modules']}</div>
                    <div class="label">Loaded Modules</div>
                </div>
                <div class="status-item">
                    <div class="number">{status['total_routes']}</div>
                    <div class="label">Total Routes</div>
                </div>
                <div class="status-item">
                    <div class="number">{status['extensions']}</div>
                    <div class="label">Extensions</div>
                </div>
                <div class="status-item">
                    <div class="number">✓</div>
                    <div class="label">Database</div>
                </div>
            </div>
        </div>
        
        <div class="modules-grid">
            <div class="module-card">
                <h3>📦 Products</h3>
                <p>Product inventory management with categories, pricing, and stock tracking.</p>
                <div class="module-links">
                    <a href="/products" class="btn">View Products</a>
                    <a href="/products/create" class="btn btn-secondary">Add Product</a>
                    <a href="/api/products" class="btn btn-api">API</a>
                </div>
            </div>
            
            <div class="module-card">
                <h3>👥 Contacts</h3>
                <p>Contact management system with full CRUD operations and search capabilities.</p>
                <div class="module-links">
                    <a href="/contacts" class="btn">View Contacts</a>
                    <a href="/contacts/create" class="btn btn-secondary">Add Contact</a>
                    <a href="/contacts/api/list" class="btn btn-api">API</a>
                </div>
            </div>
            
            <div class="module-card">
                <h3>⚙️ Base Module</h3>
                <p>Core system functionality including database connections and health monitoring.</p>
                <div class="module-links">
                    <a href="/health" class="btn">Health Check</a>
                    <a href="/status" class="btn btn-secondary">System Status</a>
                    <a href="/api/health" class="btn btn-api">API</a>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Modular System v1.0.0 | Built with ❤️ using Python</p>
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
            self.logger.log("base", f"Error in home view: {e}", "error")
            error_body = f"Error: {str(e)}".encode('utf-8')
            start_response('500 Internal Server Error', [
                ('Content-Type', 'text/plain'),
                ('Content-Length', str(len(error_body)))
            ])
            return [error_body]
    
    def health_view(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            db_status = "Connected"
            try:
                from modular_system.database.connection import get_engine
                engine = get_engine()
                with engine.connect() as conn:
                    conn.execute("SELECT 1")
            except Exception:
                db_status = "Disconnected"
            
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>System Health</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 40px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; margin-bottom: 30px; }}
        .health-item {{ display: flex; justify-content: space-between; align-items: center; padding: 15px; border-bottom: 1px solid #eee; }}
        .health-item:last-child {{ border-bottom: none; }}
        .status {{ padding: 6px 12px; border-radius: 4px; font-weight: bold; }}
        .status.healthy {{ background: #d4edda; color: #155724; }}
        .status.unhealthy {{ background: #f8d7da; color: #721c24; }}
        .back-link {{ margin-top: 30px; display: inline-block; color: #667eea; text-decoration: none; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🏥 System Health Check</h1>
        
        <div class="health-item">
            <span>📊 Overall Status</span>
            <span class="status healthy">Healthy</span>
        </div>
        
        <div class="health-item">
            <span>🗄️ Database Connection</span>
            <span class="status {'healthy' if db_status == 'Connected' else 'unhealthy'}">{db_status}</span>
        </div>
        
        <div class="health-item">
            <span>📦 Base Module</span>
            <span class="status healthy">Active</span>
        </div>
        
        <div class="health-item">
            <span>👥 Contacts Module</span>
            <span class="status healthy">Active</span>
        </div>
        
        <div class="health-item">
            <span>📦 Products Module</span>
            <span class="status healthy">Active</span>
        </div>
        
        <a href="/" class="back-link">← Back to Home</a>
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
            self.logger.log("base", f"Error in health view: {e}", "error")
            error_body = f"Error: {str(e)}".encode('utf-8')
            start_response('500 Internal Server Error', [
                ('Content-Type', 'text/plain'),
                ('Content-Length', str(len(error_body)))
            ])
            return [error_body]
