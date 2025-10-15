# Настройка Integrated Windows Authentication (IWA)

## Обзор
Этот проект теперь поддерживает автоматическую аутентификацию пользователей через Windows Authentication. Пользователи будут автоматически входить в систему с помощью своих доменных учетных данных без необходимости ввода логина/пароля.

## Что было добавлено

### 1. Модуль аутентификации (`backend/auth.py`)
- Автоматическое извлечение информации о пользователе из заголовков HTTP
- Поддержка различных заголовков аутентификации
- Интеграция с Flask через middleware
- Отладочная информация для диагностики

### 2. Обновленная конфигурация (`backend/config.py`)
- Настройки для включения/отключения Windows Authentication
- Режим отладки для диагностики проблем

### 3. API endpoints
- `/api/user` - получение информации о текущем пользователе
- `/debug/auth` - отладочная информация (только в режиме отладки)

### 4. Обновленный интерфейс
- Автоматическое отображение имени пользователя в заголовке
- Поддержка переменных шаблона для пользовательской информации

## Настройка на сервере

### Вариант 1: IIS + FastCGI (Рекомендуется для Windows Server)

1. **Установите IIS и FastCGI:**
   ```powershell
   # Включите компоненты IIS
   Enable-WindowsOptionalFeature -Online -FeatureName IIS-WebServerRole, IIS-WebServer, IIS-CommonHttpFeatures, IIS-HttpErrors, IIS-HttpLogging, IIS-RequestFiltering, IIS-StaticContent, IIS-DefaultDocument, IIS-DirectoryBrowsing, IIS-ASPNET45, IIS-NetFxExtensibility45, IIS-ISAPIExtensions, IIS-ISAPIFilter, IIS-HttpCompressionStatic, IIS-HttpCompressionDynamic, IIS-Security, IIS-RequestFiltering, IIS-Performance, IIS-WebServerManagementTools, IIS-ManagementConsole, IIS-IIS6ManagementCompatibility, IIS-Metabase, IIS-WMICompatibility, IIS-LegacyScripts, IIS-LegacySnapIn, IIS-FTPExtensibility, IIS-FTPServer, IIS-FTPManagement, IIS-WebDAV, IIS-ApplicationDevelopment, IIS-NetFxExtensibility, IIS-ISAPIExtensions, IIS-ISAPIFilter, IIS-ASPNET, IIS-CGI, IIS-FastCGI
   ```

2. **Настройте аутентификацию в IIS:**
   - Откройте IIS Manager
   - Выберите ваш сайт
   - Двойной клик на "Authentication"
   - Отключите "Anonymous Authentication"
   - Включите "Windows Authentication"

3. **Настройте FastCGI:**
   - Установите wfastcgi: `pip install wfastcgi`
   - Настройте FastCGI в IIS для Python

4. **Скопируйте файл `web.config`** в корень приложения

### Вариант 2: Nginx + Reverse Proxy (для Linux сервера)

1. **Настройте Nginx:**
   ```nginx
   server {
       listen 80;
       server_name your-intranet-site;
       
       location / {
           proxy_pass http://localhost:5000;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           proxy_set_header X-Forwarded-Host $server_name;
           proxy_set_header X-Remote-User $remote_user;
           
           # Аутентификация через Kerberos
           auth_gss on;
           auth_gss_keytab /etc/krb5.keytab;
           auth_gss_realm YOUR.DOMAIN;
           auth_gss_service_name HTTP;
       }
   }
   ```

### Вариант 3: Apache + mod_auth_kerb

1. **Установите mod_auth_kerb:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install libapache2-mod-auth-kerb
   
   # CentOS/RHEL
   sudo yum install mod_auth_kerb
   ```

2. **Настройте Apache:**
   ```apache
   <VirtualHost *:80>
       ServerName your-intranet-site
       
       <Location />
           AuthType Kerberos
           AuthName "Windows Authentication"
           KrbAuthRealms YOUR.DOMAIN
           Krb5Keytab /etc/krb5.keytab
           Require valid-user
           
           # Передача заголовков в Flask
           RequestHeader set X-Remote-User %{REMOTE_USER}s
       </Location>
       
       ProxyPreserveHost On
       ProxyPass / http://localhost:5000/
       ProxyPassReverse / http://localhost:5000/
   </VirtualHost>
   ```

## Настройка клиентских машин

### Групповые политики (GPO)
1. **Добавьте сайт в Trusted Sites:**
   - Computer Configuration → Policies → Windows Settings → Internet Explorer Maintenance → Security → Security Zones and Content Ratings
   - Добавьте ваш сайт в зону "Trusted sites"

2. **Настройте автоматический вход:**
   - Computer Configuration → Policies → Administrative Templates → Windows Components → Internet Explorer → Internet Control Panel → Security Page → Intranet Zone
   - Включите "Automatic logon with current user name and password"

### Ручная настройка браузера
1. Откройте Internet Explorer
2. Tools → Internet Options → Security
3. Выберите "Local intranet" → Sites → Advanced
4. Добавьте ваш сайт
5. Вернитесь в Security → Local intranet → Custom level
6. В разделе "User Authentication" выберите "Automatic logon with current user name and password"

## Тестирование

### 1. Проверка отладочной информации
Включите режим отладки в `web.config`:
```xml
<add key="WINDOWS_AUTH_DEBUG" value="true" />
```

Затем перейдите на `/debug/auth` для просмотра заголовков и информации о пользователе.

### 2. Проверка API
Перейдите на `/api/user` для получения JSON с информацией о текущем пользователе.

### 3. Проверка интерфейса
Имя пользователя должно автоматически отображаться в правом верхнем углу страницы.

## Переменные окружения

- `WINDOWS_AUTH_ENABLED` - включить/отключить Windows Authentication (по умолчанию: true)
- `WINDOWS_AUTH_DEBUG` - включить режим отладки (по умолчанию: false)
- `FLASK_ENV` - окружение Flask (development/production)

## Устранение неполадок

### Проблема: Пользователь не определяется
1. Проверьте заголовки в `/debug/auth`
2. Убедитесь, что Windows Authentication включен в IIS
3. Проверьте настройки браузера для автоматического входа

### Проблема: 401 Unauthorized
1. Убедитесь, что пользователь входит в домен
2. Проверьте настройки делегирования Kerberos
3. Убедитесь, что сайт добавлен в Trusted Sites

### Проблема: Заголовки не передаются
1. Проверьте настройки прокси-сервера
2. Убедитесь, что заголовки правильно настроены в конфигурации веб-сервера

## Безопасность

- Отключите режим отладки в продакшене
- Используйте HTTPS для передачи аутентификационных данных
- Настройте правильные заголовки безопасности в `web.config`
- Регулярно обновляйте сертификаты Kerberos
