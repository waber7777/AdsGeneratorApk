#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для получения информации о приложениях и рекламных блоках из Яндекс.Директ
"""

import requests
import json
from typing import List, Dict, Optional

class YandexAdsAPI:
    def __init__(self, oauth_token: str):
        """
        Инициализация API клиента
        
        Args:
            oauth_token: OAuth токен из https://oauth.yandex.ru/
        """
        self.oauth_token = oauth_token
        self.base_url = "https://partner.yandex.ru/api/v1"
        self.headers = {
            "Authorization": f"OAuth {oauth_token}",
            "Content-Type": "application/json"
        }
    
    def get_apps(self) -> Optional[List[Dict]]:
        """
        Получает список всех приложений
        
        Returns:
            Список приложений или None при ошибке
        """
        url = f"{self.base_url}/apps"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data.get('apps', [])
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении списка приложений: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Ответ сервера: {e.response.text}")
            return None
    
    def get_app_details(self, app_id: str) -> Optional[Dict]:
        """
        Получает детальную информацию о приложении
        
        Args:
            app_id: ID приложения
            
        Returns:
            Информация о приложении или None при ошибке
        """
        url = f"{self.base_url}/apps/{app_id}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении информации о приложении {app_id}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Ответ сервера: {e.response.text}")
            return None
    
    def get_ad_units(self, app_id: str) -> Optional[List[Dict]]:
        """
        Получает список рекламных блоков для приложения
        
        Args:
            app_id: ID приложения
            
        Returns:
            Список рекламных блоков или None при ошибке
        """
        url = f"{self.base_url}/apps/{app_id}/ad_units"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return data.get('ad_units', [])
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении рекламных блоков для {app_id}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Ответ сервера: {e.response.text}")
            return None
    
    def get_statistics(self, app_id: str, date_from: str, date_to: str) -> Optional[Dict]:
        """
        Получает статистику по приложению
        
        Args:
            app_id: ID приложения
            date_from: Дата начала в формате YYYY-MM-DD
            date_to: Дата окончания в формате YYYY-MM-DD
            
        Returns:
            Статистика или None при ошибке
        """
        url = f"{self.base_url}/statistics"
        params = {
            "app_id": app_id,
            "date_from": date_from,
            "date_to": date_to
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении статистики для {app_id}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Ответ сервера: {e.response.text}")
            return None
    
    def export_apps_to_configs(self, output_file: str = "apps_export.json"):
        """
        Экспортирует информацию о приложениях в JSON файл
        
        Args:
            output_file: Имя выходного файла
        """
        apps = self.get_apps()
        if not apps:
            print("Не удалось получить список приложений")
            return
        
        export_data = []
        
        for app in apps:
            app_id = app.get('id')
            app_name = app.get('name', 'Unknown')
            package_name = app.get('package_name', '')
            
            print(f"\nОбрабатываю приложение: {app_name} (ID: {app_id})")
            
            # Получаем рекламные блоки
            ad_units = self.get_ad_units(app_id)
            
            rewarded_id = None
            interstitial_id = None
            
            if ad_units:
                for unit in ad_units:
                    unit_type = unit.get('type', '').lower()
                    unit_id = unit.get('id')
                    
                    if 'rewarded' in unit_type:
                        rewarded_id = unit_id
                    elif 'interstitial' in unit_type:
                        interstitial_id = unit_id
            
            app_data = {
                "app_id": app_id,
                "app_name": app_name,
                "package_name": package_name,
                "platform": app.get('platform', 'android'),
                "rewarded_ad_unit_id": rewarded_id or "demo-rewarded-yandex",
                "interstitial_ad_unit_id": interstitial_id or "demo-interstitial-yandex",
                "status": app.get('status', 'unknown')
            }
            
            export_data.append(app_data)
            print(f"  Rewarded ID: {app_data['rewarded_ad_unit_id']}")
            print(f"  Interstitial ID: {app_data['interstitial_ad_unit_id']}")
        
        # Сохраняем в файл
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ Экспортировано {len(export_data)} приложений в {output_file}")
    
    def generate_build_configs(self, apps_file: str = "apps_export.json", 
                               keystore_name: str = "test-release.keystore",
                               key_alias: str = "testkey",
                               keystore_password: str = "password123"):
        """
        Генерирует конфигурационные файлы для сборки APK
        
        Args:
            apps_file: Файл с экспортированными приложениями
            keystore_name: Имя keystore файла
            key_alias: Алиас ключа
            keystore_password: Пароль keystore
        """
        try:
            with open(apps_file, 'r', encoding='utf-8') as f:
                apps = json.load(f)
        except FileNotFoundError:
            print(f"Файл {apps_file} не найден")
            return
        
        configs = []
        
        for i, app in enumerate(apps, 1):
            # Генерируем package name если его нет
            package_name = app.get('package_name')
            if not package_name:
                package_name = f"com.test.ads{i}"
            
            config = {
                "app_name": app['app_name'],
                "package_name": package_name,
                "version_code": 1,
                "version_name": "1.0",
                "rewarded_ad_unit_id": app['rewarded_ad_unit_id'],
                "interstitial_ad_unit_id": app['interstitial_ad_unit_id'],
                "keystore_name": keystore_name,
                "key_alias": key_alias,
                "keystore_password": keystore_password,
                "key_password": keystore_password
            }
            
            # Сохраняем каждый конфиг отдельно
            config_file = f"app_config_{i}.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            configs.append(config)
            print(f"✓ Создан {config_file}")
        
        print(f"\n✓ Создано {len(configs)} конфигурационных файлов")
        return configs


def main():
    print("="*60)
    print("  ЭКСПОРТ ПРИЛОЖЕНИЙ ИЗ ЯНДЕКС.ДИРЕКТ")
    print("="*60)
    print()
    
    # Читаем токен из файла или запрашиваем
    token_file = "yandex_token.txt"
    
    try:
        with open(token_file, 'r') as f:
            oauth_token = f.read().strip()
        print(f"✓ Токен загружен из {token_file}")
    except FileNotFoundError:
        print(f"Файл {token_file} не найден.")
        print("\nСоздайте файл yandex_token.txt и поместите в него OAuth токен")
        print("Получить токен: https://oauth.yandex.ru/")
        print("\nИли введите токен сейчас:")
        oauth_token = input("OAuth токен: ").strip()
        
        if not oauth_token:
            print("Токен не указан. Выход.")
            return
        
        # Сохраняем токен
        with open(token_file, 'w') as f:
            f.write(oauth_token)
        print(f"✓ Токен сохранён в {token_file}")
    
    print()
    
    # Создаём API клиент
    api = YandexAdsAPI(oauth_token)
    
    # Экспортируем приложения
    print("Получаю список приложений...")
    api.export_apps_to_configs()
    
    print()
    
    # Генерируем конфиги для сборки
    print("Генерирую конфигурационные файлы для сборки...")
    api.generate_build_configs()
    
    print()
    print("="*60)
    print("  ГОТОВО!")
    print("="*60)
    print("\nТеперь можно собрать APK:")
    print("  1. Скопируйте нужный app_config_N.json в app_config.json")
    print("  2. Запустите: python rebuild_app.py")
    print("\nИли используйте массовую сборку (если есть скрипт)")


if __name__ == "__main__":
    main()





