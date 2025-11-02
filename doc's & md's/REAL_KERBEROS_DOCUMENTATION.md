# Real Kerberos Authentication System

## Обзор

Реальная Kerberos-интеграция выполнена на базе pyspnego (SPNEGO/Kerberos) с опциональным обогащением ФИО из Active Directory через ldap3 (LDAP).

## Архитектура

### Основные компоненты

1. `backend/real_kerberos_auth.py` — реальная аутентификация Kerberos (pyspnego)
2. `backend/simplified_real_kerberos_auth.py` — fallback на упрощённую auth (dev)
3. `KerberosUser` — модель учётной записи Kerberos в БД
4. `KerberosSession` — модель сессий (при необходимости)

### Приоритет аутентификации

1. Kerberos (заголовок `Authorization: Negotiate ...`)
2. Fallback на упрощённую (dev), если инициализация real Kerberos не удалась
3. Guest — если нет токена

## Конфигурация

Переменные окружения (см. `backend/config.py`):

```
KERBEROS_AUTH_ENABLED=true
KERBEROS_SERVICE_NAME=HTTP
KERBEROS_REALM=EXAMPLE.COM
KERBEROS_KEYTAB=/etc/krb5.keytab
KERBEROS_KDC_HOST=localhost
KERBEROS_KDC_PORT=88

LDAP_ENABLED=true
LDAP_SERVER=ldap://dc1.example.com
LDAP_BASE_DN=DC=example,DC=com
LDAP_USER=
LDAP_PASSWORD=
```

krb5.conf пример (см. `site/krb5.conf`):
```
[libdefaults]
    default_realm = EXAMPLE.COM
    dns_lookup_realm = false
    dns_lookup_kdc = false

[realms]
    EXAMPLE.COM = {
        kdc = localhost:88
        admin_server = localhost:749
    }

[domain_realm]
    .example.com = EXAMPLE.COM
    example.com = EXAMPLE.COM
```

## Реальная аутентификация (pyspnego)

- `real_kerberos_auth.py` обрабатывает SPNEGO handhshake, извлекает `principal` (`username@REALM`), формирует `g.user_info`.
- При успехе: `username`, `principal`, `domain`, `role`, `auth_method=kerberos`.
- Роль берётся из БД (`KerberosUser.role`) при наличии записи, иначе `user`.

## LDAP/AD обогащение (ldap3)

- При включённом LDAP система ищет пользователя в AD по `sAMAccountName={username}` и подставляет `displayName` (ФИО) в `g.user_info.full_name`.
- Настройки: `LDAP_SERVER`, `LDAP_BASE_DN`, `LDAP_USER`, `LDAP_PASSWORD`.

## Тестовая AD (минимум для проверки ФИО)

Создайте OU и пользователей с полем `displayName`:

Пример LDIF (замените `DC=example,DC=com` на ваш DN):
```
dn: OU=TestUsers,DC=example,DC=com
objectClass: organizationalUnit
ou: TestUsers

dn: CN=Ivan Petrov,OU=TestUsers,DC=example,DC=com
objectClass: user
sAMAccountName: ivan.petrov
displayName: Иван Петров
userPrincipalName: ivan.petrov@example.com

dn: CN=Maria Sidorova,OU=TestUsers,DC=example,DC=com
objectClass: user
sAMAccountName: maria.sidorova
displayName: Мария Сидорова
userPrincipalName: maria.sidorova@example.com
```

## Точки интеграции

- Инициализация в `backend/__init__.py`: попытка real Kerberos, далее fallback.
- Контекст пользователя в `g.user_info` используется всеми эндпоинтами/маршрутами.

## Отладка

- Проверьте, что браузер отправляет Negotiate (SPNEGO) заголовки.
- Логи аутентификации пишутся стандартным логгером Flask.
- При проблемах с LDAP временно установите `LDAP_ENABLED=false`.

## Зависимости

```
pyspnego>=0.12.0
ldap3>=2.9
cryptography>=46.0.0
```
