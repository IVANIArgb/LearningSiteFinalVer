@echo off
REM Скрипт для настройки Kerberos окружения на Windows

echo 🔐 Настройка Kerberos окружения...

REM Создание директорий
if not exist kerberos mkdir kerberos
if not exist kerberos\keytabs mkdir kerberos\keytabs
if not exist kerberos\logs mkdir kerberos\logs
if not exist kerberos\conf mkdir kerberos\conf

REM Копирование конфигурации
copy krb5.conf kerberos\conf\

REM Установка переменных окружения
set KRB5_CONFIG=kerberos\conf\krb5.conf
set KRB5_KDC_PROFILE=kerberos\conf\kdc.conf

echo ✅ Kerberos окружение настроено
echo 📁 Конфигурация: kerberos\conf\
echo 🔑 Keytabs: kerberos\keytabs\
echo 📝 Логи: kerberos\logs\

REM Создание тестового keytab файла (пустой)
echo. > kerberos\keytabs\http.keytab
echo 🔑 Создан тестовый keytab файл

echo.
echo 🚀 Для запуска приложения используйте:
echo set KRB5_CONFIG=kerberos\conf\krb5.conf
echo python run.py

pause
