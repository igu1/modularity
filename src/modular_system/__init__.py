"""
Modular System - A flexible, extensible web framework.

A production-ready modular architecture for building scalable web applications
with pluggable modules, services, and extensions.
"""

__version__ = "1.0.0"
__author__ = "Modular System Team"

from .core.application import ModularSystem
from .core.registry import Registry
from .core.environment import Environment
from .database.connection import init_db, get_session
from .logging.logger import CoreLogger

__all__ = [
    "ModularSystem",
    "Registry", 
    "Environment",
    "init_db",
    "get_session",
    "CoreLogger"
]
