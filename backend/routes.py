import os
from typing import Dict, List, Tuple
from flask import Flask, send_from_directory, abort, redirect, Response, render_template, jsonify


def _page_map(base_path: str, allowed_dirs: List[str]) -> Dict[str, Tuple[str, str]]:
    """Map route name to (directory, index file)."""
    mapping: Dict[str, Tuple[str, str]] = {}
    for dir_name in allowed_dirs:
        if not os.path.isdir(os.path.join(base_path, dir_name)):
            continue
        route_name = dir_name.replace("-pg", "").replace("_", "-")
        mapping[route_name] = (dir_name, "index.html")
    return mapping


def _split_head_body(html: str) -> Dict[str, str]:
    """Extract <head> stylesheet hrefs and body inner HTML, then strip old header/footer.
    This preserves original visuals while avoiding duplicate header/footer.
    """
    lower = html.lower()
    head_start = lower.find("<head")
    head_end = lower.find("</head>")
    body_start = lower.find("<body")
    body_end = lower.rfind("</body>")

    head_html = html[head_start:head_end] if (head_start != -1 and head_end != -1) else ""
    body_html = html[body_start:body_end] if (body_start != -1 and body_end != -1) else html

    import re

    # collect stylesheet hrefs
    hrefs = re.findall(r'<link[^>]+rel=["\']stylesheet["\'][^>]*href=["\']([^"\']+)["\']', head_html, flags=re.I)
    page_styles = [h for h in hrefs if not h.startswith("http")]

    # strip <body ...> wrapper
    body_inner = re.sub(r"^<body[^>]*>\s*", "", body_html, flags=re.I)

    # remove first <header ...>...</header>
    body_inner = re.sub(r"<header[^>]*class=\"[^\"]*header[^\"]*\"[\s\S]*?</header>\s*", "", body_inner, count=1, flags=re.I)

    # remove last footer block and optional following made-by div
    # remove any <div class="made-by">...</div>
    body_inner = re.sub(r"<div[^>]*class=\"[^\"]*made-by[^\"]*\"[\s\S]*?</div>\s*", "", body_inner, flags=re.I)
    # remove the last footer occurrence
    footers = list(re.finditer(r"<footer[\s\S]*?</footer>", body_inner, flags=re.I))
    if footers:
        last = footers[-1]
        body_inner = body_inner[: last.start()] + body_inner[last.end() :]

    return {"page_styles": page_styles, "body_inner": body_inner}


def register_routes(app: Flask) -> None:
    base_path = app.config["PROJECT_ROOT"]
    allowed_dirs = app.config["ALLOWED_PAGE_DIRS"]
    admin_template_dir = app.config["ADMIN_TEMPLATE_DIR"]
    user_template_dir = app.config["USER_TEMPLATE_DIR"]
    
    # Создаем карты страниц для обеих ролей
    admin_pages = _page_map(os.path.join(base_path, admin_template_dir), allowed_dirs)
    user_pages = _page_map(os.path.join(base_path, user_template_dir), allowed_dirs)
    
    def _get_pages_for_user_role():
        """Get pages map based on current user role."""
        from flask import g
        user_info = g.get('user_info', {})
        user_role = user_info.get('role', 'user')
        
        # Если пользователь не аутентифицирован, используем роль 'user' по умолчанию
        if not user_info:
            user_role = 'user'
        
        # Определяем страницы на основе роли пользователя
        if user_role == 'admin':
            return admin_pages, os.path.join(base_path, admin_template_dir)
        else:
            return user_pages, os.path.join(base_path, user_template_dir)

    # Healthcheck for load balancers and uptime checks
    @app.get("/healthz")
    def healthcheck():
        return {"status": "ok"}, 200

    # Debug endpoint for Kerberos Authentication
    @app.get("/debug/kerberos")
    def debug_kerberos():
        """Debug endpoint to check Kerberos authentication info."""
        if not app.config.get('KERBEROS_AUTH_DEBUG', False):
            abort(404)
        
        from flask import g
        user_info = g.get('user_info', {})
        
        return jsonify({
            "user_info": user_info,
            "config": {
                "kerberos_auth_enabled": app.config.get('KERBEROS_AUTH_ENABLED', True),
                "kerberos_service_name": app.config.get('KERBEROS_SERVICE_NAME', 'HTTP'),
                "kerberos_realm": app.config.get('KERBEROS_REALM', 'EXAMPLE.COM')
            }
        })

    # API endpoint to get current user info - moved to api.py to avoid duplication

    # Serve templates (header, footer, CSS, images) - ролевая система
    @app.get("/templates/<path:template_path>")
    def serve_template(template_path: str):
        # Определяем роль пользователя
        from flask import g
        user_info = g.get('user_info', {})
        user_role = user_info.get('role', 'user')
        
        # Выбираем папку шаблонов в зависимости от роли
        if user_role == 'admin':
            templates_dir = os.path.join(base_path, "admin-pages", "templates")
        else:
            templates_dir = os.path.join(base_path, "user-pages", "templates")
        
        return send_from_directory(templates_dir, template_path)

    # Serve backend templates (CSS, images from backend/templates)
    @app.get("/backend/templates/<path:template_path>")
    def serve_backend_template(template_path: str):
        backend_templates_dir = os.path.join(base_path, "backend", "templates")
        return send_from_directory(backend_templates_dir, template_path)

    # User info test JSON endpoint
    @app.get("/user/info-test")
    def user_info_test():
        from flask import g
        from .models import db_manager, User, KerberosUser
        
        info = g.get('user_info', {}) or {}
        if not info.get('username'):
            return jsonify({'error': 'Пользователь не аутентифицирован'}), 401
        
        username = info.get('username')
        payload = {
            'authenticated': True,
            'username': username,
            'role': info.get('role', 'user'),
            'auth_method': info.get('auth_method'),
            'ip_address': info.get('ip_address'),
            'hostname': info.get('hostname'),
        }
        
        # Добавляем данные из g.user_info (из контекста аутентификации)
        if 'full_name' in info:
            payload['full_name'] = info.get('full_name')
        if 'surname' in info:
            payload['surname'] = info.get('surname')
        if 'fst_name' in info:
            payload['fst_name'] = info.get('fst_name')
        if 'sec_name' in info:
            payload['sec_name'] = info.get('sec_name')
        if 'department' in info:
            payload['department'] = info.get('department')
        if 'position' in info:
            payload['position'] = info.get('position')
        if 'principal' in info:
            payload['principal'] = info.get('principal')
        if 'domain' in info:
            payload['domain'] = info.get('domain')
        
        # Дополняем данными из БД (приоритет БД над контекстом)
        try:
            session = db_manager.get_session()
            try:
                # Пробуем получить данные из KerberosUser
                ku = session.query(KerberosUser).filter(KerberosUser.username == username.lower()).first()
                if ku:
                    payload['surname'] = ku.surname or payload.get('surname', '')
                    payload['fst_name'] = ku.fst_name or payload.get('fst_name', '')
                    payload['sec_name'] = ku.sec_name or payload.get('sec_name', '')
                    payload['department'] = ku.department or payload.get('department', '')
                    payload['position'] = ku.position or payload.get('position', '')
                    payload['full_name'] = ku._get_full_name_from_parts() or ku.full_name or payload.get('full_name', '')
                    payload['role'] = ku.role
                    payload['email'] = ku.email or ''
                    payload['last_login'] = ku.last_login.isoformat() if ku.last_login else None
                else:
                    # Если нет KerberosUser, пробуем User
                    user = session.query(User).filter(User.username == username.lower()).first()
                    if user:
                        payload['surname'] = user.surname or payload.get('surname', '')
                        payload['fst_name'] = user.fst_name or payload.get('fst_name', '')
                        payload['sec_name'] = user.sec_name or payload.get('sec_name', '')
                        payload['department'] = user.department or payload.get('department', '')
                        payload['position'] = user.position or payload.get('position', '')
                        payload['full_name'] = user._get_full_name_from_parts() or user.full_name or payload.get('full_name', '')
                        payload['email'] = user.email or ''
            finally:
                session.close()
        except Exception as e:
            # Если ошибка при получении данных из БД, просто логируем
            import logging
            logging.getLogger(__name__).warning(f"Failed to get user data from DB: {e}")
        
        return jsonify(payload)

    # Serve uploaded files (Q&A attachments)
    @app.get("/uploads/<path:filename>")
    def serve_upload(filename: str):
        uploads_dir = os.path.join(base_path, "backend", "api.py")  # placeholder to compute backend dir
        backend_dir = os.path.dirname(uploads_dir)
        uploads_path = os.path.join(backend_dir, "uploads")
        if not os.path.exists(os.path.join(uploads_path, filename)):
            abort(404)
        return send_from_directory(uploads_path, filename)

    # Root redirect to main page
    @app.get("/")
    def root_redirect():
        return redirect("/main-pg/", code=302)

    def _render_static_page(dir_name: str, filename: str, template_base_path: str = None):
        if template_base_path is None:
            template_base_path = base_path
        abs_dir = os.path.join(template_base_path, dir_name)
        index_path = os.path.join(abs_dir, filename)
        try:
            with open(index_path, "r", encoding="utf-8") as f:
                html = f.read()
        except FileNotFoundError:
            abort(404)
        parts = _split_head_body(html)
        
        # Определяем роль пользователя для выбора шаблона
        from flask import g
        user_info = g.get('user_info', {})
        user_role = user_info.get('role', 'user')
        
        # Выбираем шаблон в зависимости от роли
        if user_role == 'admin':
            template_name = "admin-pages/templates/base_static_page.html"
        else:
            template_name = "user-pages/templates/base_static_page.html"
        
        # Получаем контекст пользователя для отображения ФИО/логина в шапке
        username_ctx = user_info.get('username') if user_info else None
        full_name_ctx = user_info.get('full_name') if user_info else None
        role_ctx = user_info.get('role') if user_info else None

        return render_template(
            template_name,
            title=None,
            page_styles=parts["page_styles"],
            page_body=parts["body_inner"],
            username=username_ctx,
            full_name=full_name_ctx,
            role=role_ctx,
        )

    # Serve pages via friendly URLs (e.g., /main, /questions)
    @app.get("/<page_key>")
    def serve_page(page_key: str):
        pages_map, template_base_path = _get_pages_for_user_role()
        page = pages_map.get(page_key)
        if not page:
            abort(404)
        directory, filename = page
        return _render_static_page(directory, filename, template_base_path)

    # Serve legacy URLs (e.g., /main-pg/, /questions-pg/)
    @app.get("/<legacy_dir>/")
    def serve_legacy_index(legacy_dir: str):
        # Allow either configured allowed dir or physically existing dir under site root
        _, template_base_path = _get_pages_for_user_role()
        abs_dir = os.path.join(template_base_path, legacy_dir)
        if legacy_dir not in allowed_dirs and not os.path.isdir(abs_dir):
            abort(404)
        return _render_static_page(legacy_dir, "index.html", template_base_path)

    # Serve assets from legacy directories (e.g., /main-pg/img/file.png) - ролевая система
    @app.get("/<legacy_dir>/<path:legacy_path>")
    def serve_legacy_asset(legacy_dir: str, legacy_path: str):
        if legacy_dir not in allowed_dirs:
            abort(404)
        
        # Определяем роль пользователя
        from flask import g
        user_info = g.get('user_info', {})
        user_role = user_info.get('role', 'user')
        
        # Выбираем базовую папку в зависимости от роли
        if user_role == 'admin':
            template_base_path = os.path.join(base_path, "admin-pages")
        else:
            template_base_path = os.path.join(base_path, "user-pages")
        
        abs_dir = os.path.join(template_base_path, legacy_dir)
        safe_path = os.path.normpath(os.path.join(abs_dir, legacy_path))
        if not safe_path.startswith(abs_dir):
            abort(403)
        if not os.path.exists(safe_path):
            abort(404)
        rel_dir = os.path.dirname(os.path.relpath(safe_path, abs_dir))
        return send_from_directory(os.path.join(abs_dir, rel_dir), os.path.basename(safe_path))

    # Serve assets from friendly URLs (e.g., /main/img/file.png) - ролевая система
    @app.get("/<page_key>/<path:asset_path>")
    def serve_asset(page_key: str, asset_path: str):
        pages_map, template_base_path = _get_pages_for_user_role()
        page = pages_map.get(page_key)
        if not page:
            abort(404)
        directory, _ = page
        abs_dir = os.path.join(template_base_path, directory)
        safe_path = os.path.normpath(os.path.join(abs_dir, asset_path))
        if not safe_path.startswith(abs_dir):
            abort(403)
        if not os.path.exists(safe_path):
            abort(404)
        rel_dir = os.path.dirname(os.path.relpath(safe_path, abs_dir))
        return send_from_directory(os.path.join(abs_dir, rel_dir), os.path.basename(safe_path))

    # Testing-only endpoint
    @app.get("/__trigger_error")
    def trigger_error():
        if not app.config.get("TESTING"):
            abort(404)
        raise RuntimeError("Test error for 500 handler")


