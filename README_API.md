# Инструкция по работе с Яндекс.Директ API

## Шаг 1: Получение OAuth токена

1. Перейдите на https://oauth.yandex.ru/
2. Создайте приложение или используйте существующее
3. Получите OAuth токен с правами доступа к Рекламной сети Яндекса
4. **ВАЖНО:** Храните токен в безопасности!

## Шаг 2: Настройка токена

Создайте файл `yandex_token.txt` в корне проекта и поместите в него токен:

```
y0_ваш_токен_здесь
```

**Или** скрипт запросит токен при первом запуске.

## Шаг 3: Экспорт приложений

Запустите скрипт для получения информации о приложениях:

```bash
python yandex_ads_api.py
```

Скрипт:
1. Получит список всех ваших приложений из Яндекс.Директ
2. Для каждого приложения найдёт рекламные блоки (Rewarded и Interstitial)
3. Создаст файл `apps_export.json` с информацией
4. Сгенерирует конфигурационные файлы `app_config_1.json`, `app_config_2.json` и т.д.

## Шаг 4: Массовая сборка APK

### Вариант А: Сборка всех APK автоматически

```bash
python mass_build.py
```

Скрипт соберёт APK для всех найденных конфигураций.

### Вариант Б: Сборка отдельных APK

```bash
# Скопируйте нужный конфиг
copy app_config_1.json app_config.json

# Соберите APK
python rebuild_app.py
```

## Структура файлов

### apps_export.json

Экспортированная информация о приложениях:

```json
[
  {
    "app_id": "12345",
    "app_name": "Моё приложение",
    "package_name": "com.example.app",
    "platform": "android",
    "rewarded_ad_unit_id": "R-M-12345678-2",
    "interstitial_ad_unit_id": "R-M-12345678-1",
    "status": "active"
  }
]
```

### app_config_N.json

Конфигурация для сборки APK:

```json
{
  "app_name": "Моё приложение",
  "package_name": "com.example.app",
  "version_code": 1,
  "version_name": "1.0",
  "rewarded_ad_unit_id": "R-M-12345678-2",
  "interstitial_ad_unit_id": "R-M-12345678-1",
  "keystore_name": "test-release.keystore",
  "key_alias": "testkey",
  "keystore_password": "password123",
  "key_password": "password123"
}
```

## API методы

### YandexAdsAPI класс

```python
from yandex_ads_api import YandexAdsAPI

api = YandexAdsAPI(oauth_token="ваш_токен")

# Получить список приложений
apps = api.get_apps()

# Получить информацию о приложении
app_details = api.get_app_details(app_id="12345")

# Получить рекламные блоки
ad_units = api.get_ad_units(app_id="12345")

# Получить статистику
stats = api.get_statistics(
    app_id="12345",
    date_from="2025-01-01",
    date_to="2025-01-31"
)

# Экспортировать всё в файлы
api.export_apps_to_configs()
api.generate_build_configs()
```

## Безопасность

⚠️ **ВАЖНО:**

1. **НЕ** публикуйте `yandex_token.txt` в Git
2. **НЕ** делитесь токеном
3. Добавьте в `.gitignore`:
   ```
   yandex_token.txt
   apps_export.json
   app_config_*.json
   ```

## Примечания

- Если у приложения нет рекламных блоков, используются тестовые ID
- Package name генерируется автоматически, если не указан
- Все APK подписываются одним keystore (можно изменить в конфигах)

## Troubleshooting

### Ошибка 401 Unauthorized
- Проверьте правильность токена
- Убедитесь, что токен не истёк
- Проверьте права доступа токена

### Ошибка 403 Forbidden
- У токена нет прав на доступ к API
- Создайте новый токен с правильными правами

### Не найдены рекламные блоки
- Убедитесь, что в приложении созданы блоки в Яндекс.Директ
- Проверьте типы блоков (Rewarded, Interstitial)

## Полезные ссылки

- [Яндекс.Директ API документация](https://yandex.ru/dev/direct/doc/dg/concepts/about.html)
- [OAuth Яндекс](https://oauth.yandex.ru/)
- [Рекламная сеть Яндекса](https://partner.yandex.ru/)





