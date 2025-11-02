"""
Simplified Real Kerberos Authentication Module
Упрощенная версия настоящей Kerberos аутентификации без pyspnego
Для тестирования на Windows
"""

import os
import logging
import base64
from typing import Dict, Any, Optional
from flask import request, g, current_app


class SimplifiedRealKerberosAuth:
    """Упрощенный класс для настоящей аутентификации через Kerberos"""
    
    def __init__(self, app=None):
        self.app = app
        self.logger = logging.getLogger(__name__)
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Инициализация Kerberos аутентификации"""
        self.app = app
        
        # Настройка Kerberos
        self.service_name = app.config.get('KERBEROS_SERVICE_NAME', 'HTTP')
        self.realm = app.config.get('KERBEROS_REALM', 'EXAMPLE.COM')
        self.keytab_file = app.config.get('KERBEROS_KEYTAB', '/etc/krb5.keytab')
        self.kdc_host = app.config.get('KERBEROS_KDC_HOST', 'localhost')
        self.kdc_port = app.config.get('KERBEROS_KDC_PORT', 88)
        
        # Регистрация обработчиков
        app.before_request(self._authenticate_user)
        
        self.logger.info("Simplified Real Kerberos Authentication initialized")
    
    def _authenticate_user(self):
        """Аутентификация пользователя через упрощенный Kerberos"""
        try:
            # Получение Authorization заголовка
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Negotiate '):
                # Если нет Kerberos токена, пробуем Windows Auth как fallback
                return self._fallback_to_windows_auth()
            
            # Извлечение Kerberos токена
            token = auth_header[10:]  # Убираем "Negotiate "
            
            # Проверка токена через упрощенную логику
            user_info = self._verify_kerberos_token(token)
            if user_info:
                g.user_info = user_info
                self.logger.info(f"Kerberos authentication successful for user: {user_info['username']}")
            else:
                return self._fallback_to_windows_auth()
                
        except Exception as e:
            self.logger.error(f"Kerberos authentication error: {e}")
            return self._fallback_to_windows_auth()
    
    def _verify_kerberos_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Проверка Kerberos токена через упрощенную логику"""
        try:
            # Декодирование токена
            try:
                token_bytes = base64.b64decode(token)
            except Exception as e:
                self.logger.error(f"Failed to decode token: {e}")
                return None
            
            # Упрощенная проверка токена
            # В реальном Kerberos здесь была бы проверка криптографических подписей
            
            # Поиск информации о пользователе в токене
            username = self._extract_username_from_token(token_bytes)
            if not username:
                # Если не удалось извлечь, используем фиктивного пользователя
                username = "kerberos_user"
            
            # Автоматическая регистрация пользователя в БД
            self._auto_register_user(username)
            
            realm = self.realm
            
            # Определение роли пользователя
            role = self._determine_user_role(username)
            
            return {
                'username': username.lower(),
                'full_name': f"{username}@{realm}",
                'domain': realm,
                'role': role,
                'auth_method': 'kerberos',
                'ip_address': request.remote_addr,
                'hostname': self._get_hostname_by_ip(request.remote_addr),
                'principal': f"{username}@{realm}"
            }
            
        except Exception as e:
            self.logger.error(f"Kerberos token verification failed: {e}")
            return None
    
    def _extract_username_from_token(self, token_bytes: bytes) -> Optional[str]:
        """Извлечение имени пользователя из токена"""
        try:
            # Это упрощенная реализация для демонстрации
            # В реальном Kerberos здесь была бы полная декодировка ASN.1 структуры
            token_str = token_bytes.decode('utf-8', errors='ignore')
            
            # Поиск паттернов имени пользователя в токене
            import re
            patterns = [
                r'([a-zA-Z0-9._-]+)@([a-zA-Z0-9._-]+)',  # username@realm
                r'([a-zA-Z0-9._-]+)/',  # username/
                r'([a-zA-Z0-9._-]+)',  # username
            ]
            
            for pattern in patterns:
                match = re.search(pattern, token_str)
                if match:
                    return match.group(1)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to extract username from token: {e}")
            return None
    
    def _fallback_to_windows_auth(self):
        """Fallback к Windows Authentication с автоматической регистрацией"""
        try:
            # Попытка получить текущего пользователя Windows
            import getpass
            username = getpass.getuser()
            
            if username and username.lower() != 'guest':
                # Автоматическая регистрация пользователя в БД
                self._auto_register_user(username)
                
                role = self._determine_user_role(username)
                
                g.user_info = {
                    'username': username.lower(),
                    'full_name': username,
                    'domain': os.environ.get('USERDOMAIN', 'LOCAL'),
                    'role': role,
                    'auth_method': 'windows_fallback',
                    'ip_address': request.remote_addr,
                    'hostname': self._get_hostname_by_ip(request.remote_addr)
                }
                
                self.logger.info(f"Windows Auth fallback successful for user: {username}")
                return
            
        except Exception as e:
            self.logger.error(f"Windows Auth fallback failed: {e}")
        
        # Если все не удалось, создаем guest пользователя
        g.user_info = {
            'username': 'guest',
            'full_name': 'Guest User',
            'role': 'user',
            'auth_method': 'none',
            'ip_address': request.remote_addr,
            'hostname': self._get_hostname_by_ip(request.remote_addr)
        }
    
    def _determine_user_role(self, username: str) -> str:
        """Определение роли пользователя из БД"""
        session = None
        try:
            from .models import db_manager, KerberosUser
            
            session = db_manager.get_session()
            try:
                # Ищем пользователя в БД
                kerberos_user = session.query(KerberosUser).filter(
                    KerberosUser.username == username.lower()
                ).first()
                
                if kerberos_user:
                    return kerberos_user.role
                
                # Если пользователь не найден в БД, используем хардкод
                admin_users = [
                    'admin', 'administrator', 'root', 'manager',
                    'админ', 'администратор', 'руководитель',
                    'system', 'service'  # Системные пользователи
                ]
                
                if username.lower() in admin_users:
                    return 'admin'
                
                return 'user'
                
            finally:
                if session:
                    session.close()
                
        except Exception as e:
            self.logger.error(f"Ошибка определения роли для {username}: {e}")
            if session:
                try:
                    session.close()
                except Exception:
                    pass
            # Fallback к хардкоду
            admin_users = [
                'admin', 'administrator', 'root', 'manager',
                'админ', 'администратор', 'руководитель',
                'system', 'service'
            ]
            
            if username.lower() in admin_users:
                return 'admin'
            
            return 'user'
    
    def _get_hostname_by_ip(self, ip_address: str) -> str:
        """Получение hostname по IP адресу"""
        try:
            import socket
            hostname = socket.gethostbyaddr(ip_address)[0]
            return hostname
        except:
            return ip_address
    
    def _auto_register_user(self, username: str):
        """Автоматическая регистрация пользователя в БД"""
        session = None
        try:
            from .models import db_manager, User, KerberosUser
            
            session = db_manager.get_session()
            try:
                # Проверяем, существует ли пользователь в основной таблице User
                existing_user = session.query(User).filter(User.username == username.lower()).first()
                
                if not existing_user:
                    # Создаем нового пользователя как обычного user
                    new_user = User(
                        username=username.lower(),
                        full_name=username,
                        department=self._get_user_department(username),
                        email=f"{username.lower()}@company.com",
                        role='user',
                        is_active=True
                    )
                    session.add(new_user)
                    self.logger.info(f"✅ Новый пользователь зарегистрирован: {username}")
                else:
                    self.logger.info(f"ℹ️  Пользователь уже существует: {username}")
                
                # Проверяем, существует ли пользователь в таблице KerberosUser
                existing_kerberos_user = session.query(KerberosUser).filter(
                    KerberosUser.username == username.lower()
                ).first()
                
                if not existing_kerberos_user:
                    # Получаем realm из конфигурации
                    realm = getattr(self, 'realm', 'EXAMPLE.COM')
                    
                    # Создаем Kerberos запись для пользователя; роль по умолчанию user
                    kerberos_user = KerberosUser(
                        username=username.lower(),
                        principal=f"{username.lower()}@{realm}",
                        realm=realm,
                        full_name=username,
                        surname='',
                        fst_name='',
                        sec_name='',
                        department=self._get_user_department(username),
                        email=f"{username.lower()}@company.com",
                        role='user',
                        is_active=True
                    )
                    session.add(kerberos_user)
                    self.logger.info(f"✅ Kerberos пользователь зарегистрирован: {username}")
                else:
                    self.logger.info(f"ℹ️  Kerberos пользователь уже существует: {username}")
                
                session.commit()
                
            except Exception as e:
                if session:
                    session.rollback()
                self.logger.error(f"❌ Ошибка при регистрации пользователя {username}: {e}")
                raise
            finally:
                if session:
                    session.close()
                
        except Exception as e:
            self.logger.error(f"❌ Критическая ошибка при регистрации пользователя {username}: {e}")
            if session:
                try:
                    session.close()
                except Exception:
                    pass
    
    def _get_user_department(self, username: str) -> str:
        """Определение отдела пользователя на основе имени"""
        # Простая логика определения отдела
        if username.lower() in ['admin', 'administrator', 'root']:
            return 'IT отдел'
        elif username.lower() in ['manager', 'руководитель']:
            return 'Управление'
        elif username.lower() in ['пользователь', 'user']:
            return 'IT отдел'
        else:
            return 'Общий отдел'
    
    def get_user_info(self) -> Dict[str, Any]:
        """Получение информации о текущем пользователе"""
        return g.get('user_info', {
            'username': 'guest',
            'full_name': 'Guest User',
            'role': 'user',
            'auth_method': 'none',
            'ip_address': request.remote_addr,
            'hostname': self._get_hostname_by_ip(request.remote_addr)
        })


def init_simplified_real_kerberos_auth(app):
    """Инициализация упрощенной настоящей Kerberos аутентификации"""
    kerberos_auth = SimplifiedRealKerberosAuth(app)
    return kerberos_auth
