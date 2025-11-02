# Kerberos Authentication Documentation

## Обзор

Система аутентификации была переделана под Kerberos протокол. Реализована имитация Kerberos для Windows окружения без реального Kerberos сервера.

## Архитектура

### Основные компоненты

1. **KerberosAuth** - основной класс аутентификации
2. **Mock Implementation** - имитация Kerberos для тестирования
3. **Fallback механизм** - переход к Windows Auth при отсутствии Kerberos токена

### Приоритет аутентификации

1. **Kerberos** (если есть токен в заголовке `Authorization: Negotiate`)
2. **Windows Auth** (fallback)
3. **Guest** (если все остальное не работает)

## Конфигурация

### Переменные окружения

```bash
# Включение/отключение Kerberos
KERBEROS_AUTH_ENABLED=true

# Настройки Kerberos
KERBEROS_SERVICE_NAME=HTTP
KERBEROS_REALM=EXAMPLE.COM
KERBEROS_KEYTAB=/etc/krb5.keytab
```

### Отключение других методов аутентификации

```bash
# Отключение Windows Auth
WINDOWS_AUTH_ENABLED=false

# Отключение MAC Auth
MAC_AUTH_ENABLED=false
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

### Обычные пользователи

Все остальные пользователи получают роль `user`.

## API Endpoints

### Получение информации о пользователе

```http
GET /api/user
```

**Ответ:**
```json
{
  "username": "kerberos_user",
  "full_name": "kerberos_user@EXAMPLE.COM",
  "domain": "EXAMPLE.COM",
  "role": "admin",
  "auth_method": "kerberos",
  "ip_address": "127.0.0.1",
  "hostname": "localhost"
}
```

## Тестирование

Запуск тестов:

```bash
python test_kerberos_auth.py
```

### Тестовые сценарии

1. **Без токена** - проверка fallback к Windows Auth
2. **С фиктивным токеном** - проверка Kerberos аутентификации
3. **Главная страница** - проверка отображения контента по ролям

## Логирование

Все события аутентификации записываются в лог:

```
2025-10-09 08:56:24,376 - backend.kerberos_auth - INFO - Kerberos Authentication (Mock) initialized
2025-10-09 08:56:24,464 - backend.kerberos_auth - INFO - Kerberos authentication successful for user: kerberos_user
```

## Безопасность

### Текущая реализация (Mock)

- Базовая проверка формата токена
- Имитация декодирования Base64
- Фиктивные пользователи для демонстрации

### Для продакшена

Для реального Kerberos потребуется:

1. **Установка Kerberos сервера**
2. **Настройка keytab файлов**
3. **Реальная криптографическая проверка токенов**
4. **Интеграция с Active Directory**

## Миграция

### От Windows Auth

1. Установить `KERBEROS_AUTH_ENABLED=true`
2. Установить `WINDOWS_AUTH_ENABLED=false`
3. Перезапустить приложение

### От MAC Auth

1. Установить `MAC_AUTH_ENABLED=false`
2. Удалить записи из таблицы `mac_address_bindings`

## Troubleshooting

### Ошибки

1. **Windows Auth fallback failed** - не критично, используется guest режим
2. **Kerberos token verification failed** - переход к fallback

### Отладка

Включить debug режим:

```bash
KERBEROS_AUTH_DEBUG=true
```

## Будущие улучшения

1. **Реальная интеграция с Kerberos**
2. **Поддержка множественных realm**
3. **Кэширование токенов**
4. **Метрики аутентификации**
