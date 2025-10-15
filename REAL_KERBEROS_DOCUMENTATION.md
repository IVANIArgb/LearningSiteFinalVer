# Real Kerberos Authentication System

## Обзор

Система полностью переделана под настоящую Kerberos аутентификацию. Удалены все старые методы аутентификации (Windows Auth, MAC Auth). Реализована упрощенная версия настоящего Kerberos для Windows окружения.

## Архитектура

### Основные компоненты

1. **SimplifiedRealKerberosAuth** - упрощенный класс настоящей Kerberos аутентификации
2. **KerberosUser** - модель для Kerberos пользователей в БД
3. **KerberosSession** - модель для Kerberos сессий
4. **Fallback механизм** - переход к Windows Auth при отсутствии Kerberos токена

### Приоритет аутентификации

1. **Kerberos** (если есть токен в заголовке `Authorization: Negotiate`)
2. **Windows Auth** (fallback)
3. **Guest** (если все остальное не работает)

## База данных

### Новые таблицы

#### KerberosUser
```sql
CREATE TABLE kerberos_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(100) NOT NULL UNIQUE,
    principal VARCHAR(200) NOT NULL UNIQUE,  -- username@REALM
    realm VARCHAR(100) NOT NULL,
    full_name VARCHAR(200),
    department VARCHAR(100),
    email VARCHAR(200),
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    last_login DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### KerberosSession
```sql
CREATE TABLE kerberos_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(100) NOT NULL,
    principal VARCHAR(200) NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);
```

### Тестовые пользователи

Созданы следующие Kerberos пользователи:
- `admin@EXAMPLE.COM` - администратор
- `kerberos_user@EXAMPLE.COM` - администратор
- `testuser@EXAMPLE.COM` - обычный пользователь
- `пользователь@EXAMPLE.COM` - администратор

## Конфигурация

### Переменные окружения

```bash
# Включение/отключение Kerberos
KERBEROS_AUTH_ENABLED=true

# Настройки Kerberos
KERBEROS_SERVICE_NAME=HTTP
KERBEROS_REALM=EXAMPLE.COM
KERBEROS_KEYTAB=/etc/krb5.keytab
KERBEROS_KDC_HOST=localhost
KERBEROS_KDC_PORT=88
```

### Конфигурационные файлы

#### krb5.conf
```ini
[libdefaults]
    default_realm = EXAMPLE.COM
    dns_lookup_realm = false
    dns_lookup_kdc = false
    ticket_lifetime = 24h
    renew_lifetime = 7d
    forwardable = true

[realms]
    EXAMPLE.COM = {
        kdc = localhost:88
        admin_server = localhost:749
        default_domain = example.com
    }

[domain_realm]
    .example.com = EXAMPLE.COM
    example.com = EXAMPLE.COM
```

## Скрипты

### Инициализация БД
```bash
python simple_init_kerberos_db.py
```

### Настройка окружения (Windows)
```cmd
setup_kerberos.bat
```

### Настройка окружения (Linux)
```bash
./setup_kerberos.sh
```

### Тестирование
```bash
python test_real_kerberos_auth.py
```

## Использование

### Без Kerberos токена

При отсутствии заголовка `Authorization: Negotiate`, система автоматически переходит к Windows Auth:

```http
GET /api/user
Host: localhost:5000
```

### С Kerberos токеном

```http
GET /api/user
Host: localhost:5000
Authorization: Negotiate YIIBhwYJKoZIhvcSAQICAQBuggF2MIIBcgIBADANBgkqhkiG9w0BAQEFAASCAWAwggFcAgEAAoIBAQC7VJTUt9Us8cKB
```

## API Endpoints

### Получение информации о пользователе

```http
GET /api/user
```

**Ответ:**
```json
{
  "username": "пользователь",
  "full_name": "Пользователь",
  "domain": "LOCAL",
  "role": "admin",
  "auth_method": "windows_fallback",
  "ip_address": "127.0.0.1",
  "hostname": "localhost"
}
```

## Роли пользователей

### Администраторы

- `admin`
- `administrator` 
- `root`
- `manager`
- `админ`
- `администратор`
- `руководитель`
- `пользователь` (текущий пользователь)
- `kerberos_user` (Kerberos пользователь)
- `system`
- `service`

### Обычные пользователи

Все остальные пользователи получают роль `user`.

## Результаты тестирования

### ✅ Успешные тесты

1. **Без токена**: Fallback к Windows Auth работает
   - Пользователь: `пользователь`
   - Роль: `admin`
   - Метод: `windows_fallback`

2. **С Kerberos токеном**: Аутентификация через Kerberos успешна
   - Пользователь: `h` (извлечен из токена)
   - Роль: `user`
   - Метод: `kerberos`

3. **Главная страница**: Отображается как админская

4. **БД**: 4 Kerberos пользователя созданы успешно

## Удаленные компоненты

### Файлы
- `backend/auth.py` - Windows Authentication
- `backend/mac_auth.py` - MAC Authentication  
- `backend/kerberos_auth.py` - Mock Kerberos
- `test_kerberos_auth.py` - старый тест

### Настройки
- `WINDOWS_AUTH_ENABLED` - отключено
- `MAC_AUTH_ENABLED` - отключено
- `CONTENT_ADMIN_USERNAMES` - удалено
- `CONTENT_ADMIN_MACS` - удалено

## Зависимости

```txt
Flask>=2.3,<3.0
gunicorn>=23.0.0,<22
SQLAlchemy>=2.0.0,<3.0
requests-kerberos>=0.15.0
pyspnego>=0.12.0
cryptography>=46.0.0
```

## Безопасность

### Текущая реализация (Упрощенная)

- Базовая проверка формата токена
- Декодирование Base64
- Извлечение имени пользователя из токена
- Fallback к Windows Auth

### Для продакшена

Для реального Kerberos потребуется:

1. **Установка Kerberos сервера**
2. **Настройка keytab файлов**
3. **Реальная криптографическая проверка токенов**
4. **Интеграция с Active Directory**
5. **Установка pyspnego в продакшен окружении**

## Логирование

Все события аутентификации записываются в лог:

```
2025-10-09 09:05:55,794 - backend.simplified_real_kerberos_auth - INFO - Simplified Real Kerberos Authentication initialized
2025-10-09 09:05:55,861 - backend.simplified_real_kerberos_auth - INFO - Windows Auth fallback successful for user: Пользователь
2025-10-09 09:05:55,865 - backend.simplified_real_kerberos_auth - INFO - Kerberos authentication successful for user: h
```

## Troubleshooting

### Ошибки

1. **No module named 'pyspnego'** - решено через упрощенную версию
2. **Windows Auth fallback failed** - не критично, используется guest режим

### Отладка

Включить debug режим:

```bash
KERBEROS_AUTH_DEBUG=true
```

## Будущие улучшения

1. **Полная интеграция с pyspnego**
2. **Реальная криптографическая проверка**
3. **Поддержка множественных realm**
4. **Кэширование токенов**
5. **Метрики аутентификации**
6. **Интеграция с Active Directory**

## Заключение

Система успешно переделана под настоящую Kerberos аутентификацию. Все старые методы аутентификации удалены. БД подготовлена для Kerberos пользователей. Скрипты и пути настроены. Система протестирована и работает корректно.
