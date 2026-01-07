# Инструкция по использованию скрипта пересборки приложения

## Быстрый старт

1. Откройте файл `app_config.json` и заполните все поля
2. Запустите скрипт: `python rebuild_app.py`
3. Готовый APK будет в корне проекта

## Файл конфигурации `app_config.json`

```json
{
  "app_name": "Название вашей игры",
  "package_name": "com.вашеимя.названиеигры",
  "version_code": 1,
  "version_name": "1.0",
  "rewarded_ad_unit_id": "R-M-XXXXXXX-2",
  "interstitial_ad_unit_id": "R-M-XXXXXXX-1",
  "keystore_name": "название-keystore.keystore",
  "key_alias": "алиас-ключа",
  "keystore_password": "пароль-keystore",
  "key_password": "пароль-ключа"
}
```

### Поля конфигурации:

- **app_name** - Название приложения (будет отображаться на устройстве)
- **package_name** - Уникальный идентификатор пакета (например: `com.mycompany.mygame`)
- **version_code** - Версия кода (целое число, увеличивается при каждом обновлении в Google Play)
- **version_name** - Версия приложения (строка, например: "1.0", "1.1.0", "2.0.1")
- **rewarded_ad_unit_id** - ID рекламного блока с вознаграждением из Яндекс.Директ
- **interstitial_ad_unit_id** - ID межстраничного рекламного блока из Яндекс.Директ
- **keystore_name** - Имя файла keystore (должен быть в корне проекта)
- **key_alias** - Алиас ключа в keystore
- **keystore_password** - Пароль для keystore файла
- **key_password** - Пароль для ключа

## Что делает скрипт:

1. ✅ Обновляет название игры во всех файлах
2. ✅ Переименовывает package name
3. ✅ Обновляет версию приложения (versionCode и versionName)
4. ✅ Перемещает Java файлы в новую структуру пакетов
5. ✅ Обновляет Ad Unit ID в рекламных блоках
6. ✅ Обновляет настройки подписи (keystore)
7. ✅ Собирает release APK

## Обновляемые файлы:

- `capacitor.config.ts` - название и ID приложения
- `package.json` - название проекта
- `index.html` - заголовок страницы
- `android/app/build.gradle` - package, версии, keystore настройки
- `android/app/src/main/res/values/strings.xml` - строки ресурсов
- `android/app/src/main/AndroidManifest.xml` - package в манифесте
- Java файлы - package и импорты
- `YandexAdsPlugin.java` - Ad Unit ID

## Требования:

- Python 3.6+
- Node.js и npm установлены
- Android SDK и Gradle настроены
- Keystore файл должен находиться в корне проекта

## Пример использования:

1. Отредактируйте `app_config.json`:
```json
{
  "app_name": "Моя Супер Игра",
  "package_name": "com.mystudio.supergame",
  "version_code": 2,
  "version_name": "1.1",
  "rewarded_ad_unit_id": "R-M-12345678-2",
  "interstitial_ad_unit_id": "R-M-12345678-1",
  "keystore_name": "supergame-release.keystore",
  "key_alias": "supergame",
  "keystore_password": "mypassword123",
  "key_password": "mypassword123"
}
```

2. Убедитесь, что keystore файл `supergame-release.keystore` находится в корне проекта

3. Запустите:
```bash
python rebuild_app.py
```

4. Готовый APK будет: `Моя_Супер_Игра-v1.1-release.apk` (версия включена в имя файла)

## Важные замечания:

⚠️ **Keystore файл** - сохраните его в безопасном месте! Без него нельзя обновлять приложение в Google Play.

⚠️ **Package name** - после публикации в Google Play его нельзя изменить!

⚠️ **Ad Unit ID** - получайте их в личном кабинете Яндекс.Директ: https://partner.yandex.ru/

⚠️ **Версия** - при обновлении приложения увеличьте `version_code` в `app_config.json` (versionCode должен быть больше предыдущего для Google Play)

## Создание нового Keystore:

Если нужно создать новый keystore:

```bash
keytool -genkey -v -keystore название-release.keystore -alias алиас -keyalg RSA -keysize 2048 -validity 10000
```

Затем укажите параметры в `app_config.json`.

