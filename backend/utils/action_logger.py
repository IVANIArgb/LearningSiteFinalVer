"""Utilities for writing user-friendly action logs."""

from __future__ import annotations

from datetime import datetime
import os
from typing import Callable, Iterable

from flask import current_app, g, request


def _ensure_log_path(log_path: str) -> None:
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    if not os.path.exists(log_path):
        with open(log_path, "w", encoding="utf-8") as log_file:
            log_file.write("=== Журнал действий пользователей ===\n")


def init_action_logger(app) -> None:
    """
    Подключает автоматическое логирование действий пользователей.
    Каждое действие сохраняется в человеко-читаемом формате.
    """
    log_path = app.config.get("USER_ACTION_LOG")
    if not log_path:
        app.logger.warning("USER_ACTION_LOG path is not configured; action logging disabled.")
        return

    _ensure_log_path(log_path)

    def _write_entry(description: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_info = getattr(g, "user_info", {}) or {}
        username = user_info.get("username") or "неизвестный пользователь"
        role = user_info.get("role") or "роль не определена"
        ip_address = request.headers.get("X-Forwarded-For", request.remote_addr) if request else "-"
        entry = f"{timestamp} | пользователь: {username} ({role}) | IP: {ip_address} | действие: {description}"
        with open(log_path, "a", encoding="utf-8") as log_file:
            log_file.write(entry + "\n")

    app.extensions["action_logger_writer"] = _write_entry

    skip_prefixes: Iterable[str] = app.config.get("ACTION_LOG_SKIP_PATHS", ())

    @app.after_request
    def _log_request(response):
        try:
            path = request.path
            if not any(path.startswith(prefix) for prefix in skip_prefixes):
                _write_entry(f"{request.method} {path} (код {response.status_code})")
        except Exception as exc:
            app.logger.debug("Не удалось записать действие: %s", exc)
        return response


def record_user_action(description: str) -> None:
    """Записать пользовательское действие в лог (используется внутри обработчиков)."""
    writer: Callable[[str], None] | None = current_app.extensions.get("action_logger_writer")  # type: ignore[arg-type]
    if writer:
        writer(description)

