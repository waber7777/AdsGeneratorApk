#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для получения информации о приложениях через API Партнерского интерфейса Яндекса
Документация: https://yandex.ru/dev/partner-statistics/doc/ru/
"""

import requests
import json
from datetime import datetime, timedelta

class YandexPartnerAPI:
    def __init__(self, oauth_token: str):
        """
        Инициализация API клиента
        
        Args:
            oauth_token: OAuth токен
        """
        self.oauth_token = oauth_token
        self.base_url = "https://partner2.yandex.ru/api/statistics2/get.json"
        self.headers = {
            "Authorization": f"OAuth {oauth_token}",
            "Content-Type": "application/json"
        }
    
    def get_statistics(self, date_from: str = None, date_to: str = None, 
                      group_by: str = "page_id", fields: list = None, pretty: bool = True):
        """
        Получает статистику
        
        Args:
            date_from: Дата начала (YYYY-MM-DD)
            date_to: Дата окончания (YYYY-MM-DD)
            group_by: Группировка (page_id, date, etc)
            fields: Список полей для получения
            pretty: Форматированный вывод
            
        Returns:
            Данные статистики
        """
        # По умолчанию последние 7 дней
        if not date_from:
            date_from = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        if not date_to:
            date_to = datetime.now().strftime('%Y-%m-%d')
        
        # Поля по умолчанию
        if not fields:
            fields = ["partner_wo_nds", "shows", "clicks", "page_views"]
        
        params = {
            "period": f"{date_from},{date_to}",  # Формат: YYYY-MM-DD,YYYY-MM-DD
            "group_by": group_by,
            "field": ",".join(fields),  # Строка через запятую
            "pretty": 1 if pretty else 0
        }
        
        try:
            print(f"Запрос к API: {self.base_url}")
            print(f"Параметры: {params}")
            
            response = requests.get(self.base_url, headers=self.headers, params=params)
            print(f"Статус: {response.status_code}")
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Ошибка: {response.status_code}")
                print(f"Ответ: {response.text}")
                return None
                
        except Exception as e:
            print(f"Исключение: {e}")
            return None
    
    def get_apps_info(self):
        """
        Получает информацию о приложениях через статистику
        """
        print("\n" + "="*60)
        print("  ПОЛУЧЕНИЕ ИНФОРМАЦИИ О ПРИЛОЖЕНИЯХ")
        print("="*60 + "\n")
        
        # Получаем статистику за последний месяц
        date_from = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        date_to = datetime.now().strftime('%Y-%m-%d')
        
        print(f"Период: {date_from} - {date_to}\n")
        
        # Пробуем разные группировки
        groupings = ["page_id", "partner_wo_nds"]
        
        all_data = {}
        
        for group in groupings:
            print(f"Получаю данные с группировкой: {group}")
            data = self.get_statistics(date_from, date_to, group)
            
            if data:
                all_data[group] = data
                print(f"✓ Получено данных для {group}")
            else:
                print(f"✗ Не удалось получить данные для {group}")
            print()
        
        return all_data
    
    def save_to_file(self, data, filename="partner_data.json"):
        """
        Сохраняет данные в файл
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"\n✓ Данные сохранены в {filename}")
            return True
        except Exception as e:
            print(f"\n✗ Ошибка при сохранении: {e}")
            return False
    
    def parse_and_extract_apps(self, data, output_file="apps_info.json"):
        """
        Парсит данные и извлекает информацию о приложениях
        """
        print("\n" + "="*60)
        print("  АНАЛИЗ ДАННЫХ")
        print("="*60 + "\n")
        
        apps_info = []
        
        # Анализируем данные
        for group_type, group_data in data.items():
            print(f"Анализ группы: {group_type}")
            
            if not group_data:
                continue
            
            # Извлекаем информацию о страницах/приложениях
            if 'data' in group_data:
                for item in group_data.get('data', []):
                    app_entry = {
                        "group_type": group_type,
                        "raw_data": item
                    }
                    
                    # Пытаемся извлечь ID и название
                    if 'page_id' in item:
                        app_entry['page_id'] = item['page_id']
                    
                    if 'name' in item:
                        app_entry['name'] = item['name']
                    
                    apps_info.append(app_entry)
            
            print(f"  Найдено записей: {len(group_data.get('data', []))}")
        
        # Сохраняем извлечённую информацию
        if apps_info:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(apps_info, f, ensure_ascii=False, indent=2)
            print(f"\n✓ Информация о приложениях сохранена в {output_file}")
            print(f"  Всего записей: {len(apps_info)}")
        else:
            print("\n⚠ Не удалось извлечь информацию о приложениях")
        
        return apps_info


def main():
    print("="*60)
    print("  ЯНДЕКС ПАРТНЕРСКИЙ ИНТЕРФЕЙС - ПОЛУЧЕНИЕ ДАННЫХ")
    print("="*60)
    print()
    
    # Читаем токен
    try:
        with open('yandex_token.txt', 'r') as f:
            token = f.read().strip()
        print("✓ Токен загружен из yandex_token.txt\n")
    except FileNotFoundError:
        print("✗ Файл yandex_token.txt не найден")
        return
    
    # Создаём API клиент
    api = YandexPartnerAPI(token)
    
    # Получаем данные
    data = api.get_apps_info()
    
    if data:
        # Сохраняем полные данные
        api.save_to_file(data, "partner_data_full.json")
        
        # Парсим и извлекаем информацию о приложениях
        apps = api.parse_and_extract_apps(data)
        
        # Выводим краткую сводку
        print("\n" + "="*60)
        print("  КРАТКАЯ СВОДКА")
        print("="*60)
        
        if apps:
            print(f"\nНайдено приложений/страниц: {len(apps)}")
            print("\nПервые 5 записей:")
            for i, app in enumerate(apps[:5], 1):
                print(f"\n{i}. {app.get('name', 'Без названия')}")
                print(f"   Page ID: {app.get('page_id', 'N/A')}")
        else:
            print("\n⚠ Данные получены, но приложения не найдены")
            print("Возможно, нужны другие параметры запроса или права доступа")
    else:
        print("\n✗ Не удалось получить данные")
        print("\nВозможные причины:")
        print("1. Неверный токен")
        print("2. Недостаточно прав у токена")
        print("3. Нет данных за указанный период")
        print("4. API изменился")
    
    print("\n" + "="*60)
    print("  ГОТОВО")
    print("="*60)


if __name__ == "__main__":
    main()

