from typing import Dict, Any
from datetime import datetime
import time
class SystemService:
    def __init__(self, module):
        self.module = module
        self.logger = module.logger
        self.start_time = time.time()
    def get_system_status(self) -> Dict[str, Any]:
        try:
            registry = getattr(self.module.env, '_registry', None)
            loaded_modules = []
            total_routes = 0
            if registry:
                loaded_modules = list(registry.modules.keys())
                total_routes = len(registry.routes)
            patch_engine = getattr(self.module.env, '_patch_engine', None)
            extensions_count = 0
            if patch_engine:
                extensions_count = len(patch_engine.applied_patches)
            db_status = self._check_database_status()
            return {
                'loaded_modules': len(loaded_modules),
                'modules': loaded_modules,
                'total_routes': total_routes,
                'extensions': extensions_count,
                'database': db_status,
                'uptime': self._get_uptime(),
                'timestamp': str(datetime.now()),
                'memory_usage': self._get_memory_usage(),
                'python_version': self._get_python_version()
            }
        except Exception as e:
            self.logger.log("base", f"Error getting system status: {e}", "error")
            return {
                'error': str(e),
                'timestamp': str(datetime.now())
            }
    def check_health(self) -> Dict[str, Any]:
        health_status = {
            'overall': 'healthy',
            'checks': {},
            'timestamp': str(datetime.now())
        }
        db_check = self._check_database_status()
        health_status['checks']['database'] = {
            'status': 'healthy' if db_check == 'connected' else 'unhealthy',
            'details': db_check
        }
        modules_check = self._check_modules_status()
        health_status['checks']['modules'] = modules_check
        memory_check = self._check_memory_status()
        health_status['checks']['memory'] = memory_check
        for check_name, check_result in health_status['checks'].items():
            if check_result.get('status') == 'unhealthy':
                health_status['overall'] = 'unhealthy'
                break
        return health_status
    def _check_database_status(self) -> str:
        try:
            from modular_system.database.connection import get_engine
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            return "connected"
        except Exception as e:
            self.logger.log("base", f"Database check failed: {e}", "warning")
            return "disconnected"
    def _check_modules_status(self) -> Dict[str, Any]:
        try:
            registry = getattr(self.module.env, '_registry', None)
            if not registry:
                return {
                    'status': 'unhealthy',
                    'details': 'Registry not available'
                }
            modules = registry.modules
            module_status = {
                'status': 'healthy',
                'loaded_count': len(modules),
                'modules': {}
            }
            for module_name, module_instance in modules.items():
                module_status['modules'][module_name] = {
                    'status': 'active',
                    'initialized': hasattr(module_instance, 'env')
                }
            return module_status
        except Exception as e:
            return {
                'status': 'unhealthy',
                'details': str(e)
            }
    def _check_memory_status(self) -> Dict[str, Any]:
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            return {
                'status': 'healthy',
                'rss_mb': round(memory_info.rss / 1024 / 1024, 2),
                'vms_mb': round(memory_info.vms / 1024 / 1024, 2),
                'percent': round(process.memory_percent(), 2)
            }
        except ImportError:
            return {
                'status': 'unknown',
                'details': 'psutil not available'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'details': str(e)
            }
    def _get_uptime(self) -> str:
        uptime_seconds = int(time.time() - self.start_time)
        hours = uptime_seconds // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    def _get_memory_usage(self) -> Dict[str, Any]:
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            return {
                'rss_mb': round(memory_info.rss / 1024 / 1024, 2),
                'vms_mb': round(memory_info.vms / 1024 / 1024, 2),
                'percent': round(process.memory_percent(), 2)
            }
        except ImportError:
            return {'error': 'psutil not available'}
        except Exception as e:
            return {'error': str(e)}
    def _get_python_version(self) -> str:
        import sys
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
