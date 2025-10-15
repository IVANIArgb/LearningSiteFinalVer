from __future__ import annotations

from typing import Any, Dict, Optional
import os

from flask import Flask

from .config import get_config
from .errors import register_error_handlers
from .routes import register_routes
from .utils.logging_config import configure_logging
from .simplified_real_kerberos_auth import init_simplified_real_kerberos_auth
from .api import init_api


def create_app(env_or_config: Optional[str | Dict[str, Any]] = None) -> Flask:
    # Flask будет искать шаблоны в корневой папке site
    # Это позволит использовать пути типа "admin-pages/templates/base_static_page.html"
    site_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    app = Flask(__name__, template_folder=site_root)

    if isinstance(env_or_config, dict):
        app.config.update(env_or_config)
    else:
        config_cls = get_config(env_or_config)
        app.config.from_object(config_cls)

    configure_logging(app)
    register_error_handlers(app)
    
    # Initialize Simplified Real Kerberos Authentication (ONLY)
    if app.config.get('KERBEROS_AUTH_ENABLED', True):
        init_simplified_real_kerberos_auth(app)
        app.logger.info("Simplified Real Kerberos Authentication initialized")
    
    # Initialize API and Database
    init_api(app)
    app.logger.info("API and Database initialized")
    
    register_routes(app)

    app.logger.info("Flask application initialized")
    return app
