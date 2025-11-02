import os


def _project_root() -> str:
    """Return absolute path to the site root used for templates and static pages.

    This backend now runs from the `site` folder. We anchor PROJECT_ROOT to
    the directory that contains the page directories and the `templates` folder.
    """
    # <repo_root>/site/backend/config.py -> <repo_root>/site
    return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
    DEBUG = False
    TESTING = False

    # Root where the existing frontend directories live
    PROJECT_ROOT = _project_root()

    # Explicitly enumerate the allowed frontend page directories
    ALLOWED_PAGE_DIRS = [
        "main-pg",
        "all-categories-pg",
        "all-courses-pg",
        "all-lessons-pg",
        "lessons-content-pg",
        "questions-pg",
        "users-info-pg",
    ]
    
    # Template directories for different user roles
    # Admin pages live in site/admin-pages; user pages in site/user-pages
    ADMIN_TEMPLATE_DIR = "admin-pages"
    USER_TEMPLATE_DIR = "user-pages"
    
    # Template directories for headers/footers based on role
    ADMIN_TEMPLATES_DIR = "admin-pages/templates"
    USER_TEMPLATES_DIR = "user-pages/templates"

    # Kerberos realm configuration
    KERBEROS_DEFAULT_REALM = "EXAMPLE.COM"

    # Logging
    LOG_DIR = os.path.join(PROJECT_ROOT, "backend", "logs")
    LOG_FILE = os.path.join(LOG_DIR, "app.log")
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    
    # Kerberos Authentication settings (REAL)
    KERBEROS_AUTH_ENABLED = os.environ.get("KERBEROS_AUTH_ENABLED", "true").lower() == "true"
    KERBEROS_SERVICE_NAME = os.environ.get("KERBEROS_SERVICE_NAME", "HTTP")
    KERBEROS_REALM = os.environ.get("KERBEROS_REALM", "EXAMPLE.COM")
    KERBEROS_KEYTAB = os.environ.get("KERBEROS_KEYTAB", "/etc/krb5.keytab")
    KERBEROS_KDC_HOST = os.environ.get("KERBEROS_KDC_HOST", "localhost")
    KERBEROS_KDC_PORT = int(os.environ.get("KERBEROS_KDC_PORT", "88"))

    # LDAP/AD enrichment
    LDAP_ENABLED = os.environ.get("LDAP_ENABLED", "true").lower() == "true"
    LDAP_SERVER = os.environ.get("LDAP_SERVER", "ldap://dc1.example.com")
    LDAP_USER = os.environ.get("LDAP_USER", "")  # e.g. user@example.com
    LDAP_PASSWORD = os.environ.get("LDAP_PASSWORD", "")
    LDAP_BASE_DN = os.environ.get("LDAP_BASE_DN", "DC=example,DC=com")
    
    # Database settings
    # БД размещается в папке backend
    _backend_dir = os.path.dirname(os.path.abspath(__file__))
    _db_path = os.path.join(_backend_dir, 'users_courses.db')
    DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{_db_path}")
    DATABASE_INIT_SAMPLE_DATA = os.environ.get("DATABASE_INIT_SAMPLE_DATA", "true").lower() == "true"


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(env_name: str = None):
    env = (env_name or os.environ.get("FLASK_ENV") or "production").lower()
    return CONFIG_MAP.get(env, ProductionConfig)








