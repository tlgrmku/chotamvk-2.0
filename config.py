#Файл конфигурации бота

#таймаут запросов к vk api (в секундах)
timeout = 120

#количество запрашиваемых постов в одном запросе
countpost = 5

#телеграм канал или чат куда бот будет отправлять посты
tgchatid = '@имя группы, канала, юзера'

#имя клиента pyrogram (может быть любым)
nameclient = 'client'

#токен vk
token='токен вконтакте'

#путь к файлу для сохранения даты последнего поста
DATESAVE = '/путь/имя файла'

#путь к лог-файлу
LOGF = '/путь/имя файла.log'

#путь к фотографии для вывода ошибки загрузки фотографии
errorphoto = '/путь/имя файла.png'

#фильтрует посты в которых имеются слова из списка. Пример словаря: ['слово', 'Слово']
ignore_words = []