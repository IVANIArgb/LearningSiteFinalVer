from __future__ import annotations

import logging
from typing import Any, Dict
from datetime import datetime
from flask import request, g

import spnego
from ldap3 import Server, Connection, ALL, NTLM
from .ad_user_info import get_user_info_by_login


class RealKerberosAuth:
    def __init__(self, app=None):
        self.app = app
        self.logger = logging.getLogger(__name__)
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        app.before_request(self._authenticate)

    def _authenticate(self):
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Negotiate '):
                # Нет Kerberos заголовка — пробуем Windows-пользователя как fallback
                try:
                    import getpass
                    username = getpass.getuser()
                    if username:
                        # Получаем данные из AD
                        ad_info = {}
                        try:
                            ad_info = get_user_info_by_login(username)
                            self.logger.info(f"AD info retrieved for {username} (Windows fallback): {ad_info}")
                        except Exception as e:
                            self.logger.warning(f"Failed to get AD info for {username}: {e}")
                        
                        # Авторегистрация в БД - создаем и User, и KerberosUser
                        session = None
                        try:
                            from .models import db_manager, User, KerberosUser
                            session = db_manager.get_session()
                            try:
                                # Подготовка данных
                                surname = ad_info.get('sur_name', '') if ad_info and ad_info.get('sur_name') not in ['Не указано', 'Ошибка'] else ''
                                fst_name = ad_info.get('first_name', '') if ad_info and ad_info.get('first_name') not in ['Не указано', 'Ошибка'] else ''
                                sec_name = ad_info.get('second_name', '') if ad_info and ad_info.get('second_name') not in ['Не указано', 'Ошибка'] else ''
                                department = ad_info.get('department', 'Общий отдел') if ad_info and ad_info.get('department') not in ['Не указано', 'Ошибка'] else 'Общий отдел'
                                position = ad_info.get('position', '') if ad_info and ad_info.get('position') not in ['Не указано', 'Ошибка'] else ''
                                
                                name_parts = [surname, fst_name, sec_name]
                                constructed_full_name = ' '.join(filter(None, name_parts)) if any(name_parts) else username
                                
                                # Определяем realm и principal для Windows fallback
                                realm = self.app.config.get('KERBEROS_REALM', 'EXAMPLE.COM')
                                principal = f"{username.lower()}@{realm}"
                                
                                # Обновляем или создаем KerberosUser
                                ku = session.query(KerberosUser).filter(KerberosUser.username == username.lower()).first()
                                if ku:
                                    # Обновляем существующего KerberosUser
                                    if surname:
                                        ku.surname = surname
                                    if fst_name:
                                        ku.fst_name = fst_name
                                    if sec_name:
                                        ku.sec_name = sec_name
                                    if department:
                                        ku.department = department
                                    if position:
                                        ku.position = position
                                    ku.full_name = constructed_full_name
                                    ku.last_login = datetime.now()
                                    ku.principal = principal
                                    ku.realm = realm
                                    self.logger.info(f"Updated KerberosUser (Windows fallback): {username.lower()}")
                                else:
                                    # Создаем нового KerberosUser
                                    ku = KerberosUser(
                                        username=username.lower(),
                                        principal=principal,
                                        realm=realm,
                                        surname=surname,
                                        fst_name=fst_name,
                                        sec_name=sec_name,
                                        full_name=constructed_full_name,
                                        department=department,
                                        position=position,
                                        email=f"{username.lower()}@company.com",
                                        role='user',
                                        is_active=True,
                                        last_login=datetime.now()
                                    )
                                    session.add(ku)
                                    self.logger.info(f"Created new KerberosUser (Windows fallback): {username.lower()}")
                                
                                # Обновляем или создаем User
                                user = session.query(User).filter(User.username == username.lower()).first()
                                if user:
                                    # Обновляем существующего User
                                    if surname:
                                        user.surname = surname
                                    if fst_name:
                                        user.fst_name = fst_name
                                    if sec_name:
                                        user.sec_name = sec_name
                                    if department:
                                        user.department = department
                                    if position:
                                        user.position = position
                                    user.full_name = constructed_full_name
                                    user.email = user.email or f"{username.lower()}@company.com"
                                    user.role = 'user'  # По умолчанию для Windows fallback
                                    self.logger.info(f"Updated User (Windows fallback): {username.lower()}")
                                else:
                                    # Создаем нового User
                                    user = User(
                                        username=username.lower(),
                                        surname=surname,
                                        fst_name=fst_name,
                                        sec_name=sec_name,
                                        full_name=constructed_full_name,
                                        department=department,
                                        position=position,
                                        email=f"{username.lower()}@company.com",
                                        role='user',  # По умолчанию для Windows fallback
                                        is_active=True
                                    )
                                    session.add(user)
                                    self.logger.info(f"Created new User (Windows fallback): {username.lower()}")
                                
                                session.commit()
                                self.logger.info(f"Successfully saved user data to DB (Windows fallback): {username.lower()}")
                            except Exception as e:
                                session.rollback()
                                self.logger.error(f"Failed to register user in DB: {e}", exc_info=True)
                            finally:
                                if session:
                                    session.close()
                        except Exception as e:
                            self.logger.error(f"Failed to register user in DB: {e}", exc_info=True)
                            if session:
                                try:
                                    session.close()
                                except Exception:
                                    pass
                        
                        # Формируем user_info
                        surname = ad_info.get('sur_name', '') if ad_info and ad_info.get('sur_name') not in ['Не указано', 'Ошибка'] else ''
                        fst_name = ad_info.get('first_name', '') if ad_info and ad_info.get('first_name') not in ['Не указано', 'Ошибка'] else ''
                        sec_name = ad_info.get('second_name', '') if ad_info and ad_info.get('second_name') not in ['Не указано', 'Ошибка'] else ''
                        department = ad_info.get('department', 'Общий отдел') if ad_info and ad_info.get('department') not in ['Не указано', 'Ошибка'] else 'Общий отдел'
                        position = ad_info.get('position', '') if ad_info and ad_info.get('position') not in ['Не указано', 'Ошибка'] else ''
                        
                        name_parts = [surname, fst_name, sec_name]
                        constructed_full_name = ' '.join(filter(None, name_parts)) if any(name_parts) else username
                        
                        g.user_info = {
                            'username': username.lower(),
                            'full_name': constructed_full_name,
                            'surname': surname,
                            'fst_name': fst_name,
                            'sec_name': sec_name,
                            'department': department,
                            'position': position,
                            'role': 'user',
                            'auth_method': 'windows_fallback',
                            'ip_address': request.remote_addr
                        }
                        return
                except Exception:
                    pass
                # Если и Windows недоступен — считаем обычным user, но без имени
                g.user_info = {'username': 'user', 'role': 'user', 'auth_method': 'none', 'ip_address': request.remote_addr}
                return

            in_token = auth_header.split(' ', 1)[1]
            server = spnego.server(service=self.app.config.get('KERBEROS_SERVICE_NAME', 'HTTP'))
            out_token = server.step(in_token)
            if out_token:
                # Client may require WWW-Authenticate: Negotiate <token>, but for simplicity skip header write here
                pass
            if not server.complete:
                self.logger.warning("SPNEGO authentication not complete")
                return

            principal = server.principal
            username = principal.split('@')[0] if principal else None
            realm = principal.split('@')[1] if principal and '@' in principal else self.app.config.get('KERBEROS_REALM', 'EXAMPLE.COM')

            # Получаем данные из AD через PowerShell скрипт
            ad_info = {}
            if username:
                try:
                    ad_info = get_user_info_by_login(username)
                    self.logger.info(f"AD info retrieved for {username}: {ad_info}")
                except Exception as e:
                    self.logger.warning(f"Failed to get AD info for {username}: {e}")

            # Enrich with LDAP if enabled
            full_name = username
            if self.app.config.get('LDAP_ENABLED', True):
                try:
                    full_name = self._ldap_display_name(username)
                except Exception as e:
                    self.logger.warning(f"LDAP enrichment failed: {e}")

            # Role resolution and user registration/update
            if not username:
                self.logger.warning("Username is None, cannot register user")
                g.user_info = {'username': 'user', 'role': 'user', 'auth_method': 'none', 'ip_address': request.remote_addr}
                return
                
            role = 'user'
            session = None
            try:
                from .models import db_manager, KerberosUser, User
                session = db_manager.get_session()
                try:
                    # Подготовка данных из AD
                    surname = ''
                    fst_name = ''
                    sec_name = ''
                    department = 'Общий отдел'
                    position = ''
                    
                    # Извлекаем данные из AD если доступны
                    if ad_info:
                        surname = ad_info.get('sur_name', '') if ad_info.get('sur_name') not in ['Не указано', 'Ошибка'] else ''
                        fst_name = ad_info.get('first_name', '') if ad_info.get('first_name') not in ['Не указано', 'Ошибка'] else ''
                        sec_name = ad_info.get('second_name', '') if ad_info.get('second_name') not in ['Не указано', 'Ошибка'] else ''
                        department = ad_info.get('department', 'Общий отдел') if ad_info.get('department') not in ['Не указано', 'Ошибка'] else 'Общий отдел'
                        position = ad_info.get('position', '') if ad_info.get('position') not in ['Не указано', 'Ошибка'] else ''
                    
                    # Если есть full_name из LDAP, но нет данных из AD, пытаемся распарсить
                    if full_name and full_name != username and not (surname or fst_name):
                        name_parts = full_name.split()
                        if len(name_parts) >= 2:
                            surname = name_parts[0]
                            fst_name = name_parts[1]
                            if len(name_parts) >= 3:
                                sec_name = name_parts[2]
                    
                    # Формируем полное имя
                    name_parts = [surname, fst_name, sec_name]
                    constructed_full_name = ' '.join(filter(None, name_parts)) if any(name_parts) else full_name
                    
                    # Обновляем или создаем KerberosUser
                    ku = session.query(KerberosUser).filter(KerberosUser.username == username.lower()).first()
                    if ku:
                        # Обновляем существующего пользователя - ВСЕГДА обновляем, даже если AD недоступен
                        if surname:
                            ku.surname = surname
                        if fst_name:
                            ku.fst_name = fst_name
                        if sec_name:
                            ku.sec_name = sec_name
                        if department:
                            ku.department = department
                        if position:
                            ku.position = position
                        ku.full_name = constructed_full_name
                        ku.last_login = datetime.now()
                        # Обновляем principal и realm на случай изменения
                        ku.principal = principal
                        ku.realm = realm
                        role = ku.role
                        self.logger.info(f"Updated KerberosUser: {username.lower()}")
                    else:
                        # Создаем нового KerberosUser
                        ku = KerberosUser(
                            username=username.lower(),
                            principal=principal,
                            realm=realm,
                            surname=surname,
                            fst_name=fst_name,
                            sec_name=sec_name,
                            full_name=constructed_full_name,
                            department=department,
                            position=position,
                            email=f"{username.lower()}@company.com",
                            role=role,
                            is_active=True,
                            last_login=datetime.now()
                        )
                        session.add(ku)
                        self.logger.info(f"Created new KerberosUser: {username.lower()}")
                    
                    # Обновляем или создаем User
                    user = session.query(User).filter(User.username == username.lower()).first()
                    if user:
                        # Обновляем существующего пользователя - ВСЕГДА обновляем
                        if surname:
                            user.surname = surname
                        if fst_name:
                            user.fst_name = fst_name
                        if sec_name:
                            user.sec_name = sec_name
                        if department:
                            user.department = department
                        if position:
                            user.position = position
                        user.full_name = constructed_full_name
                        user.email = user.email or f"{username.lower()}@company.com"
                        # Синхронизируем роль из KerberosUser
                        user.role = role
                        self.logger.info(f"Updated User: {username.lower()}")
                    else:
                        # Создаем нового User
                        user = User(
                            username=username.lower(),
                            surname=surname,
                            fst_name=fst_name,
                            sec_name=sec_name,
                            full_name=constructed_full_name,
                            department=department,
                            position=position,
                            email=f"{username.lower()}@company.com",
                            role=role,
                            is_active=True
                        )
                        session.add(user)
                        self.logger.info(f"Created new User: {username.lower()}")
                    
                    session.commit()
                    self.logger.info(f"Successfully saved user data to DB: {username.lower()}")
                except Exception as e:
                    if session:
                        session.rollback()
                    self.logger.error(f"Failed to update user in DB: {e}", exc_info=True)
                finally:
                    if session:
                        session.close()
            except Exception as e:
                self.logger.error(f"Database operation failed: {e}", exc_info=True)
                if session:
                    try:
                        session.close()
                    except Exception:
                        pass

            # Формируем g.user_info с данными из AD
            surname = ad_info.get('sur_name', '') if ad_info and ad_info.get('sur_name') not in ['Не указано', 'Ошибка'] else ''
            fst_name = ad_info.get('first_name', '') if ad_info and ad_info.get('first_name') not in ['Не указано', 'Ошибка'] else ''
            sec_name = ad_info.get('second_name', '') if ad_info and ad_info.get('second_name') not in ['Не указано', 'Ошибка'] else ''
            department = ad_info.get('department', 'Общий отдел') if ad_info and ad_info.get('department') not in ['Не указано', 'Ошибка'] else 'Общий отдел'
            position = ad_info.get('position', '') if ad_info and ad_info.get('position') not in ['Не указано', 'Ошибка'] else ''
            
            name_parts = [surname, fst_name, sec_name]
            constructed_full_name = ' '.join(filter(None, name_parts)) if any(name_parts) else full_name

            g.user_info = {
                'username': username.lower() if username else None,
                'full_name': constructed_full_name,
                'surname': surname,
                'fst_name': fst_name,
                'sec_name': sec_name,
                'department': department,
                'position': position,
                'domain': realm,
                'role': role,
                'auth_method': 'kerberos',
                'ip_address': request.remote_addr,
                'principal': principal
            }
        except Exception as e:
            self.logger.error(f"Kerberos auth error: {e}")
            g.user_info = {'username': 'user', 'role': 'user', 'auth_method': 'none', 'ip_address': request.remote_addr}

    def _ldap_display_name(self, username: str) -> str:
        server_uri = self.app.config.get('LDAP_SERVER')
        base_dn = self.app.config.get('LDAP_BASE_DN')
        bind_user = self.app.config.get('LDAP_USER')
        bind_pass = self.app.config.get('LDAP_PASSWORD')

        server = Server(server_uri, get_info=ALL)
        if bind_user and bind_pass:
            conn = Connection(server, user=bind_user, password=bind_pass, authentication=NTLM, auto_bind=True)
        else:
            conn = Connection(server, auto_bind=True)
        conn.search(base_dn, f'(sAMAccountName={username})', attributes=['displayName', 'cn'])
        try:
            entry = conn.entries[0]
            return str(entry.displayName or entry.cn or username)
        except Exception:
            return username


def init_real_kerberos_auth(app):
    RealKerberosAuth(app)
    return app


