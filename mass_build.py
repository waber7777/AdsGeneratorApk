#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для массовой сборки APK из нескольких конфигов
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

def build_from_config(config_file: str) -> bool:
    """
    Собирает APK из конфигурационного файла
    
    Args:
        config_file: Путь к файлу конфигурации
        
    Returns:
        True если сборка успешна, False иначе
    """
    config_path = Path(config_file)
    if not config_path.exists():
        print(f"✗ Файл {config_file} не найден")
        return False
    
    # Копируем конфиг в app_config.json
    shutil.copy(config_path, "app_config.json")
    print(f"✓ Скопирован {config_file} → app_config.json")
    
    # Запускаем rebuild_app.py
    try:
        result = subprocess.run(
            [sys.executable, "rebuild_app.py"],
            check=True,
            capture_output=False
        )
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"✗ Ошибка при сборке: {e}")
        return False

def main():
    print("="*60)
    print("  МАССОВАЯ СБОРКА APK")
    print("="*60)
    print()
    
    # Ищем все конфигурационные файлы
    config_files = sorted(Path(".").glob("app_config_*.json"))
    
    if not config_files:
        print("✗ Не найдено конфигурационных файлов app_config_*.json")
        print("\nСначала запустите: python yandex_ads_api.py")
        return
    
    print(f"Найдено {len(config_files)} конфигурационных файлов:")
    for config in config_files:
        try:
            with open(config, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"  - {config.name}: {data.get('app_name', 'Unknown')}")
        except:
            print(f"  - {config.name}: (ошибка чтения)")
    
    print()
    response = input("Начать сборку всех APK? (y/n): ").strip().lower()
    
    if response != 'y':
        print("Отменено")
        return
    
    print()
    print("="*60)
    
    successful = 0
    failed = 0
    
    for i, config_file in enumerate(config_files, 1):
        print()
        print(f"[{i}/{len(config_files)}] Сборка из {config_file.name}...")
        print("-"*60)
        
        if build_from_config(str(config_file)):
            successful += 1
            print(f"✓ [{i}/{len(config_files)}] Успешно")
        else:
            failed += 1
            print(f"✗ [{i}/{len(config_files)}] Ошибка")
    
    print()
    print("="*60)
    print("  ИТОГИ СБОРКИ")
    print("="*60)
    print(f"Успешно: {successful}")
    print(f"Ошибок: {failed}")
    print(f"Всего: {len(config_files)}")
    print()
    
    # Показываем собранные APK
    apk_files = list(Path(".").glob("*-release.apk"))
    if apk_files:
        print("Собранные APK:")
        for apk in sorted(apk_files):
            size_mb = apk.stat().st_size / (1024 * 1024)
            print(f"  - {apk.name} ({size_mb:.2f} MB)")

if __name__ == "__main__":
    main()





