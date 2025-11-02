"""
Модуль для получения информации о пользователях из Active Directory через PowerShell.
"""

import subprocess
import json
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Кэш для проверки наличия модуля ActiveDirectory
_ad_module_available = None


def _check_ad_module_available() -> bool:
    """Проверяет, доступен ли модуль ActiveDirectory PowerShell."""
    global _ad_module_available
    if _ad_module_available is not None:
        return _ad_module_available
    
    try:
        result = subprocess.run(
            ['powershell', '-Command', 'Get-Module -ListAvailable -Name ActiveDirectory'],
            capture_output=True,
            text=True,
            timeout=5
        )
        _ad_module_available = result.returncode == 0 and 'ActiveDirectory' in result.stdout
        return _ad_module_available
    except Exception:
        _ad_module_available = False
        return False


class ADUserInfo:
    """Класс для получения информации о пользователе из Active Directory."""
    
    def __init__(self, login: str):
        self.login = login
        self.data: Dict[str, any] = {}
        self.error: Optional[str] = None
    
    def _escape_powershell_string(self, value: str) -> str:
        """Экранирует строку для безопасного использования в PowerShell команде."""
        if not value:
            return '""'
        escaped = value.replace("'", "''")
        return f"'{escaped}'"
    
    def _fetch_user_data(self) -> bool:
        """Получает данные пользователя из AD через PowerShell."""
        if not _check_ad_module_available():
            logger.debug("ActiveDirectory PowerShell module not available, skipping AD query")
            return False
        
        try:
            escaped_login = self._escape_powershell_string(self.login)
            command = f'''
            Import-Module ActiveDirectory -ErrorAction SilentlyContinue
            $login = {escaped_login}
            try {{
                $user = Get-ADUser -Identity $login -Properties GivenName, Surname, MiddleName, Name,
                        DisplayName, Department, Title, Company, Office, Description -ErrorAction Stop
                $user | Select-Object GivenName, Surname, MiddleName, Name, DisplayName,
                        Department, Title, Company, Office, Description |
                ConvertTo-Json -Depth 1
            }} catch {{
                exit 1
            }}
            '''
            
            result = subprocess.run(
                ['powershell', '-Command', command],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                logger.debug(f"PowerShell command failed for user {self.login}: {result.stderr}")
                return False
            
            if not result.stdout or not result.stdout.strip():
                logger.debug(f"No output from PowerShell for user {self.login}")
                return False
            
            try:
                self.data = json.loads(result.stdout)
                return True
            except json.JSONDecodeError as e:
                logger.debug(f"Failed to parse JSON from PowerShell output: {e}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.debug(f"PowerShell command timeout for user {self.login}")
            return False
        except Exception as e:
            logger.debug(f"Error executing PowerShell command: {e}")
            return False
    
    def _extract_basic_info(self):
        """Извлекает базовую информацию из данных AD."""
        given_name = self.data.get('GivenName', '')
        surname = self.data.get('Surname', '')
        middle_name = self.data.get('MiddleName', '')
        display_name = self.data.get('DisplayName', '')
        
        return {
            'first_name': given_name or '',
            'sur_name': surname or '',
            'second_name': middle_name or '',
            'display_name': display_name or ''
        }
    
    def _extract_middle_name(self):
        """Извлекает отчество из различных источников."""
        middle_name = self.data.get('MiddleName', '')
        if middle_name:
            return middle_name
        
        display_name = self.data.get('DisplayName', '')
        if display_name:
            name_parts = display_name.split()
            if len(name_parts) >= 3:
                return name_parts[2]
        
        return ''
    
    def _extract_department(self) -> str:
        """Извлекает отдел из данных AD."""
        department = self.data.get('Department', '')
        if department:
            return department
        
        # Пробуем найти в других полях
        description = self.data.get('Description', '')
        if 'отдел' in description.lower() or 'department' in description.lower():
            return description
        
        return 'Общий отдел'
    
    def _extract_position(self) -> str:
        """Извлекает должность из данных AD."""
        title = self.data.get('Title', '')
        if title:
            return title
        
        return ''
    
    def get_user_info(self) -> Dict[str, any]:
        """Получает информацию о пользователе."""
        if not self._fetch_user_data():
            return {
                'first_name': 'Не указано',
                'sur_name': 'Не указано',
                'second_name': 'Не указано',
                'department': 'Не указано',
                'position': 'Не указано',
                'error': 'AD data not available'
            }
        
        basic_info = self._extract_basic_info()
        middle_name = self._extract_middle_name()
        department = self._extract_department()
        position = self._extract_position()
        
        return {
            'first_name': basic_info['first_name'] or 'Не указано',
            'sur_name': basic_info['sur_name'] or 'Не указано',
            'second_name': middle_name or 'Не указано',
            'department': department or 'Общий отдел',
            'position': position or '',
            'display_name': basic_info.get('display_name', '')
        }


def get_user_info_by_login(login: str) -> Dict[str, any]:
    """
    Получить информацию о пользователе из Active Directory по логину.
    
    Args:
        login: Логин пользователя
        
    Returns:
        Словарь с информацией о пользователе:
        - first_name: Имя
        - sur_name: Фамилия
        - second_name: Отчество
        - department: Отдел
        - position: Должность
        - display_name: Отображаемое имя
    """
    ad_user = ADUserInfo(login)
    return ad_user.get_user_info()
