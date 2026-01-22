#!/usr/bin/env python3
"""
Скрипт синхронизации данных с PythonAnywhere
"""
import requests
import os
import sys
from datetime import datetime
import json

class PythonAnywhereSync:
    def __init__(self, username, api_token):
        self.username = username
        self.api_token = api_token
        self.base_url = f"https://www.pythonanywhere.com/api/v0/user/{username}"
        self.headers = {'Authorization': f'Token {api_token}'}
    
    def upload_file(self, local_path, remote_path):
        """Загрузка файла на PythonAnywhere"""
        try:
            if not os.path.exists(local_path):
                print(f"⚠️ Файл не найден: {local_path}")
                return False
            
            # Читаем файл
            with open(local_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Проверяем, что это валидный JSON (для отладки)
            try:
                json.loads(content)
                print(f"✓ JSON валиден: {os.path.basename(local_path)}")
            except json.JSONDecodeError as e:
                print(f"⚠️ Внимание: невалидный JSON в {local_path}: {e}")
            
            files_url = f"{self.base_url}/files/path{remote_path}"
            
            # Удаляем старый файл если существует
            print(f"  Удаляю старый файл...")
            delete_response = requests.delete(files_url, headers=self.headers)
            
            # Загружаем новый файл
            print(f"  Загружаю новый файл...")
            response = requests.post(
                files_url,
                headers=self.headers,
                files={'content': content}
            )
            
            if response.status_code == 201:
                print(f"  ✅ Файл загружен: {os.path.basename(local_path)}")
                return True
            else:
                print(f"  ❌ Ошибка загрузки: {response.status_code} - {response.text[:100]}")
                return False
                
        except Exception as e:
            print(f"  ❌ Исключение: {e}")
            return False

def main():
    print(f"\n{'='*60}")
    print(f"🔄 СИНХРОНИЗАЦИЯ С PYTHONANYWHERE")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    # Получаем секреты
    username = os.environ.get('PYTHONANYWHERE_USERNAME')
    api_token = os.environ.get('PYTHONANYWHERE_API_TOKEN')
    
    if not username or not api_token:
        print("❌ Ошибка: секреты не установлены")
        print("Проверьте наличие секретов в GitHub:")
        print("  - PYTHONANYWHERE_USERNAME")
        print("  - PYTHONANYWHERE_API_TOKEN")
        sys.exit(1)
    
    print(f"👤 Пользователь: {username}")
    print(f"🔑 Токен (первые 10 символов): {api_token[:10]}...")
    
    # Создаем синхронизатор
    sync = PythonAnywhereSync(username, api_token)
    
    # Файлы для синхронизации
    files = [
        ('data/atr_latest.json', '/home/Konst2004new/atr_dashboard/data/atr_latest.json'),
        ('data/atr_baseline.json', '/home/Konst2004new/atr_dashboard/data/atr_baseline.json'),
        ('data/monitoring_current.json', '/home/Konst2004new/atr_dashboard/data/monitoring_current.json')
    ]
    
    # Синхронизируем
    success = 0
    total = len(files)
    
    for local, remote in files:
        print(f"\n📄 Обработка: {local}")
        print(f"  → {remote}")
        if sync.upload_file(local, remote):
            success += 1
    
    print(f"\n{'='*60}")
    print(f"📊 ИТОГ:")
    print(f"✅ Успешно: {success}/{total} файлов")
    
    if success == total:
        print("🎯 Все файлы синхронизированы успешно!")
        sys.exit(0)
    elif success > 0:
        print(f"⚠️ Частично успешно ({success}/{total})")
        sys.exit(0)  # Все равно выходим с кодом 0, если хоть что-то загрузилось
    else:
        print("❌ Синхронизация не удалась")
        sys.exit(1)

if __name__ == "__main__":
    main()