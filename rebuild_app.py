#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для автоматического переименования приложения и сборки APK
Использование: python rebuild_app.py
"""

import json
import os
import shutil
import subprocess
import re
from pathlib import Path

# Цвета для вывода
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_step(message):
    print(f"{Colors.BLUE}>>> {message}{Colors.END}")

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

def load_config():
    """Загружает конфигурацию из app_config.json"""
    config_path = Path("app_config.json")
    if not config_path.exists():
        print_error("Файл app_config.json не найден!")
        print("Создайте файл app_config.json с нужными параметрами.")
        exit(1)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Проверка обязательных полей
    required_fields = ['app_name', 'package_name', 'rewarded_ad_unit_id', 
                      'interstitial_ad_unit_id', 'keystore_name']
    for field in required_fields:
        if field not in config:
            print_error(f"Отсутствует обязательное поле: {field}")
            exit(1)
    
    return config

def update_file(file_path, replacements):
    """Обновляет файл, заменяя все вхождения по словарю replacements"""
    file_path = Path(file_path)
    if not file_path.exists():
        print_warning(f"Файл не найден: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print_error(f"Ошибка при обновлении {file_path}: {e}")
        return False

def update_regex_file(file_path, patterns):
    """Обновляет файл используя регулярные выражения"""
    file_path = Path(file_path)
    if not file_path.exists():
        print_warning(f"Файл не найден: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        for pattern, replacement in patterns.items():
            content = re.sub(pattern, replacement, content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print_error(f"Ошибка при обновлении {file_path}: {e}")
        return False

def get_old_package():
    """Определяет текущий package из build.gradle"""
    build_gradle = Path("android/app/build.gradle")
    if build_gradle.exists():
        with open(build_gradle, 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r'namespace\s*=\s*"([^"]+)"', content)
            if match:
                return match.group(1)
    return "com.neonsnake.game"

def move_java_files(old_package, new_package):
    """Перемещает Java файлы в новую структуру пакетов"""
    if old_package == new_package:
        return True
    
    old_path = Path("android/app/src/main/java") / old_package.replace('.', '/')
    new_path = Path("android/app/src/main/java") / new_package.replace('.', '/')
    
    if not old_path.exists():
        print_warning(f"Старая структура пакетов не найдена: {old_path}")
        return False
    
    try:
        # Создаём новую структуру
        new_path.mkdir(parents=True, exist_ok=True)
        
        # Перемещаем файлы
        for java_file in old_path.glob("*.java"):
            shutil.move(str(java_file), str(new_path / java_file.name))
            print_success(f"Перемещён: {java_file.name}")
        
        # Удаляем старую структуру если пуста
        try:
            old_path.rmdir()
            parent = old_path.parent
            while parent != Path("android/app/src/main/java") and not any(parent.iterdir()):
                parent.rmdir()
                parent = parent.parent
        except:
            pass
        
        return True
    except Exception as e:
        print_error(f"Ошибка при перемещении Java файлов: {e}")
        return False

def update_capacitor_config(config):
    """Обновляет capacitor.config.ts"""
    print_step("Обновление capacitor.config.ts")
    config_path = Path("capacitor.config.ts")
    if not config_path.exists():
        print_warning("capacitor.config.ts не найден")
        return
    
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Заменяем appId (любое значение)
    content = re.sub(
        r"appId:\s*'[^']+'",
        f"appId: '{config['package_name']}'",
        content
    )
    
    # Заменяем appName (любое значение)
    content = re.sub(
        r"appName:\s*'[^']+'",
        f"appName: '{config['app_name']}'",
        content
    )
    
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print_success("capacitor.config.ts обновлён")

def update_package_json(config):
    """Обновляет package.json"""
    print_step("Обновление package.json")
    replacements = {
        '"name": "snake-game"': f'"name": "{config["package_name"].replace(".", "-").replace("com-", "")}"',
        '"description": "Неоновый Змей - классическая змейка с современным дизайном"': f'"description": "{config["app_name"]} - описание"'
    }
    update_file("package.json", replacements)
    print_success("package.json обновлён")

def update_index_html(config):
    """Обновляет index.html"""
    print_step("Обновление index.html")
    html_path = Path("index.html")
    if not html_path.exists():
        print_warning("index.html не найден")
        return
    
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Заменяем title (любое значение между <title> и </title>)
    content = re.sub(
        r"<title>[^<]+</title>",
        f"<title>{config['app_name']}</title>",
        content
    )
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print_success("index.html обновлён")

def update_build_gradle(config, old_package):
    """Обновляет android/app/build.gradle"""
    print_step("Обновление build.gradle")
    
    # Читаем файл
    build_gradle = Path("android/app/build.gradle")
    with open(build_gradle, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Замены package
    replacements = {
        f'namespace = "{old_package}"': f'namespace = "{config["package_name"]}"',
        f'applicationId "{old_package}"': f'applicationId "{config["package_name"]}"'
    }
    
    # Обновление версий
    if 'version_code' in config:
        version_code_pattern = r"versionCode\s+\d+"
        content = re.sub(version_code_pattern, f"versionCode {config['version_code']}", content)
    
    if 'version_name' in config:
        version_name_pattern = r'versionName\s+"[^"]+"'
        content = re.sub(version_name_pattern, f'versionName "{config["version_name"]}"', content)
    
    # Обновление keystore
    keystore_pattern = r"storeFile file\('\.\.\/\.\.\/[^']+'\)"
    keystore_replacement = f"storeFile file('../../{config['keystore_name']}')"
    content = re.sub(keystore_pattern, keystore_replacement, content)
    
    # Обновление паролей если указаны
    if 'keystore_password' in config:
        password_pattern = r"storePassword '[^']+'"
        content = re.sub(password_pattern, f"storePassword '{config['keystore_password']}'", content)
    
    if 'key_password' in config:
        key_password_pattern = r"keyPassword '[^']+'"
        content = re.sub(key_password_pattern, f"keyPassword '{config['key_password']}'", content)
    
    if 'key_alias' in config:
        alias_pattern = r"keyAlias '[^']+'"
        content = re.sub(alias_pattern, f"keyAlias '{config['key_alias']}'", content)
    
    # Записываем обратно
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    with open(build_gradle, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print_success("build.gradle обновлён")

def update_strings_xml(config):
    """Обновляет android/app/src/main/res/values/strings.xml"""
    print_step("Обновление strings.xml")
    strings_path = Path("android/app/src/main/res/values/strings.xml")
    if not strings_path.exists():
        print_warning("strings.xml не найден")
        return
    
    with open(strings_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Заменяем app_name
    content = re.sub(
        r'<string name="app_name">[^<]+</string>',
        f'<string name="app_name">{config["app_name"]}</string>',
        content
    )
    
    # Заменяем title_activity_main
    content = re.sub(
        r'<string name="title_activity_main">[^<]+</string>',
        f'<string name="title_activity_main">{config["app_name"]}</string>',
        content
    )
    
    # Заменяем package_name
    content = re.sub(
        r'<string name="package_name">[^<]+</string>',
        f'<string name="package_name">{config["package_name"]}</string>',
        content
    )
    
    # Заменяем custom_url_scheme
    content = re.sub(
        r'<string name="custom_url_scheme">[^<]+</string>',
        f'<string name="custom_url_scheme">{config["package_name"]}</string>',
        content
    )
    
    with open(strings_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print_success("strings.xml обновлён")

def update_android_manifest(config, old_package):
    """Обновляет AndroidManifest.xml"""
    print_step("Обновление AndroidManifest.xml")
    manifest_path = Path("android/app/src/main/AndroidManifest.xml")
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Удаляем package атрибут (в новых версиях AGP используется namespace из build.gradle)
    # Удаляем package="..." из открывающего тега manifest
    content = re.sub(r'\s+package="[^"]+"', '', content)
    # Если package был на отдельной строке, удаляем всю строку
    content = re.sub(r'\s*package="[^"]+"\s*\n', '', content)
    
    with open(manifest_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print_success("AndroidManifest.xml обновлён")

def update_java_files(config, old_package):
    """Обновляет Java файлы"""
    print_step("Обновление Java файлов")
    
    new_package = config['package_name']
    if old_package == new_package:
        print_warning("Package не изменился, пропускаем перемещение файлов")
    else:
        if not move_java_files(old_package, new_package):
            print_error("Не удалось переместить Java файлы")
            return False
    
    # Обновляем package в Java файлах
    java_path = Path("android/app/src/main/java") / new_package.replace('.', '/')
    
    for java_file in java_path.glob("*.java"):
        with open(java_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Заменяем package
        content = re.sub(
            r'package\s+[^;]+;',
            f'package {new_package};',
            content
        )
        
        # Заменяем импорты старого пакета
        if old_package != new_package:
            content = content.replace(f'import {old_package}.', f'import {new_package}.')
        
        with open(java_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print_success(f"Обновлён: {java_file.name}")

def update_yandex_ads_plugin(config):
    """Обновляет Ad Unit ID в YandexAdsPlugin.java"""
    print_step("Обновление YandexAdsPlugin.java")
    
    new_package = config['package_name']
    plugin_path = Path("android/app/src/main/java") / new_package.replace('.', '/') / "YandexAdsPlugin.java"
    
    if not plugin_path.exists():
        print_error(f"Файл не найден: {plugin_path}")
        return False
    
    with open(plugin_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Обновляем Ad Unit ID
    content = re.sub(
        r'REWARDED_AD_UNIT_ID\s*=\s*"[^"]+"',
        f'REWARDED_AD_UNIT_ID = "{config["rewarded_ad_unit_id"]}"',
        content
    )
    
    content = re.sub(
        r'INTERSTITIAL_AD_UNIT_ID\s*=\s*"[^"]+"',
        f'INTERSTITIAL_AD_UNIT_ID = "{config["interstitial_ad_unit_id"]}"',
        content
    )
    
    with open(plugin_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print_success("YandexAdsPlugin.java обновлён")

def build_apk(config):
    """Собирает release APK"""
    print_step("Сборка release APK")
    
    # Проверяем наличие keystore
    keystore_path = Path(config['keystore_name'])
    if not keystore_path.exists():
        print_error(f"Keystore файл не найден: {keystore_path}")
        print_warning("Продолжаем сборку без проверки keystore...")
        print_warning("Убедитесь, что keystore файл находится в корне проекта!")
    
    # Синхронизация Capacitor
    print_step("Синхронизация Capacitor...")
    try:
        # Используем shell=True для Windows
        result = subprocess.run(["npm", "run", "build"], check=True, cwd=Path.cwd(), shell=True)
        result = subprocess.run(["npx", "cap", "sync", "android"], check=True, cwd=Path.cwd(), shell=True)
        print_success("Capacitor синхронизирован")
    except subprocess.CalledProcessError as e:
        print_error(f"Ошибка синхронизации Capacitor: {e}")
        return False
    except FileNotFoundError:
        print_error("npm не найден в PATH. Убедитесь, что Node.js установлен.")
        return False
    
    # Сборка APK
    print_step("Сборка Android APK...")
    try:
        android_dir = Path("android")
        os.chdir(android_dir)
        subprocess.run([".\\gradlew.bat", "clean"], check=True, shell=True)
        subprocess.run([".\\gradlew.bat", "assembleRelease"], check=True, shell=True)
        os.chdir("..")
        print_success("APK собран успешно!")
        
        # Копируем APK в корень
        apk_path = Path("android/app/build/outputs/apk/release/app-release.apk")
        if apk_path.exists():
            app_name_safe = config['app_name'].replace(' ', '_').replace('/', '_')
            version_suffix = ""
            if 'version_name' in config:
                version_suffix = f"-v{config['version_name']}"
            elif 'version_code' in config:
                version_suffix = f"-v{config['version_code']}"
            output_apk = Path(f"{app_name_safe}{version_suffix}-release.apk")
            shutil.copy(apk_path, output_apk)
            size_mb = apk_path.stat().st_size / (1024 * 1024)
            print_success(f"APK скопирован: {output_apk} ({size_mb:.2f} MB)")
            return True
        else:
            print_error("APK файл не найден после сборки")
            return False
    except subprocess.CalledProcessError as e:
        os.chdir("..")
        print_error(f"Ошибка сборки APK: {e}")
        return False

def main():
    print(f"{Colors.BLUE}{'='*60}")
    print("  АВТОМАТИЧЕСКАЯ ПЕРЕСБОРКА ПРИЛОЖЕНИЯ")
    print(f"{'='*60}{Colors.END}\n")
    
    # Загружаем конфигурацию
    config = load_config()
    print_success("Конфигурация загружена")
    print(f"  Название: {config['app_name']}")
    print(f"  Пакет: {config['package_name']}")
    if 'version_code' in config:
        print(f"  Version Code: {config['version_code']}")
    if 'version_name' in config:
        print(f"  Version Name: {config['version_name']}")
    print(f"  Rewarded ID: {config['rewarded_ad_unit_id']}")
    print(f"  Interstitial ID: {config['interstitial_ad_unit_id']}")
    print(f"  Keystore: {config['keystore_name']}\n")
    
    # Определяем старый package
    old_package = get_old_package()
    print(f"Текущий package: {old_package}\n")
    
    # Обновляем файлы
    update_capacitor_config(config)
    update_package_json(config)
    update_index_html(config)
    update_build_gradle(config, old_package)
    update_strings_xml(config)
    update_android_manifest(config, old_package)
    update_java_files(config, old_package)
    update_yandex_ads_plugin(config)
    
    print()
    print_step("Все файлы обновлены. Начинаем сборку...\n")
    
    # Собираем APK
    if build_apk(config):
        print()
        print(f"{Colors.GREEN}{'='*60}")
        print("  СБОРКА ЗАВЕРШЕНА УСПЕШНО!")
        print(f"{'='*60}{Colors.END}")
    else:
        print()
        print(f"{Colors.RED}{'='*60}")
        print("  ОШИБКА ПРИ СБОРКЕ!")
        print(f"{'='*60}{Colors.END}")
        exit(1)

if __name__ == "__main__":
    main()

