# Обновлённый бот Telegram-канала "Чо там Вконтакте?"

## Бот копирует посты из новостной ленты аккаунта Вконтакте и размещает их в Telegram канале/группе/в личных сообщениях.

### О боте:
 - Весь код написан на Python 3.8.10
 - Используемые методы vk api: newsfeed.get.
 - Используемые методы telegram api: sendMessage, sendPhoto, sendAnimation.
 - Используемые библиотеки: requests, json, time, re, os.path, logging, [Pyrogram](https://docs.pyrogram.org/).
 - Каждый пост в telegram имеет кнопку-ссылку на оригинальный пост вконтакте.
 - Игнорирует посты с пометкой "Реклама" и репосты.
 - Фильтр постов по ключевым словам настраивается в файле config.py.
 - Использует только одно фото, видео, файл из поста.
 - Интервал запросов настраивается в файле config.py.
 - Количество постов в одном запросе настраивается в файле config.py.
 - Ведение лога ошибок.

> Telegram канал который ведёт бот: https://t.me/chotamvk

> Telegram автора бота: https://t.me/tlgrmku
