# yt-telegram-archiver

## Описание
Небольшой прототип приложения для подписки на youtube каналы. При появлении новых роликов скачивает видео и загружает в telegram-канал.

## Перед установкой
1. Получите bot_token через @botfather
2. Получите api_id и api_hash здесь https://core.telegram.org/api/obtaining_api_id
3. Создайте **публичный** канал в telegram, куда будут загружаться видео с youtube
4. Если у вас нет аккаунта на heroku.com, создайте его (на своем хостинге поднимать веселее, но дольше)

## Легкая быстрая установка на heroku
1. Перейдите по ссылке https://heroku.com/deploy
2. Придумайте название приложения латинскими буквами без пробелов(можно дефисы) - будет создан субдомен с таким же именем.
3. Заполните поля Config Vars
* APP_NAME - должен совпадать с названием приложения, которое вы придумали.
* MONGODB_PASSWORD, MONGODB_USER, MONGODB_SOCKET_PATH можно не заполнять
* PROD_ENV можно не менять
* SIMPLELOGIN_USERNAME - придумайте имя пользователя для админки (по умолчанию admin)
* SIMPLELOGIN_PASSWORD - придумайте пароль для админки
* TELEGRAM_API_HASH и TELEGRAM_API_ID- значения, которые вы получили на странице https://core.telegram.org/api/obtaining_api_id
* TELEGRAM_ARCHIVE_CHANNEL_USERNAME - название публичного канала, куда будут загружены видео.
* TELEGRAM_BOT_TOKEN - токен, полученный через @botfather
* TELEGRAM_USERNAME - ваш собственный username в telegram
4. Нажмите Deploy app и подождите завершения установки
5. После завершения установки админка будет доступна по адресу https://<название_приложения>.herokuapp.com/admin

## Настройка подписки на каналы.
1. Перейдите во вкладку Overview, в разделе add-ons нажмите на Heroku scheduler.
2. Нажмите Add new job и введите в строку команду ```python src/subscriptiontask.py``` и выставите частоту обновления(frequency) в значение daily,
затем нажмите save.

## Добавление каналов
1. Авторизуйтесь по адресу https://<название_приложения>.herokuapp.com/admin
2. Перейдите во вкладку channels и нажмите кнопку create
3. Укажите channel_id, его можно взять на странице youtube канала (например https://www.youtube.com/channel/UCtI0Hodo5o5dUb67FeUjDeA), где UCtI0Hodo5o5dUb67FeUjDeA - id канала.
4. Укажите название канала (можно вписать любое)
5. Нажмите Save
