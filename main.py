import config
import requests
import json
import time
import re
import os.path
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging


timeout = config.timeout
countpost = config.countpost
tgchatid = config.tgchatid
adminchat = config.adminchat
nameclient = config.nameclient
token= config.token
DATESAVE = config.DATESAVE
LOGF = config.LOGF
errorphoto = config.errorphoto
ignore_words = config.ignore_words
URL = f'https://api.vk.com/method/newsfeed.get?filters=post&count={countpost}&access_token={token}&v=5.131'
FORMAT = '%(asctime)s : %(message)s'
logging.basicConfig(level=logging.WARNING, filename=LOGF, format=FORMAT)

log = logging.getLogger()

#Строки api_id, api_hash, bot_token, app=... нужны для первого запуска бота. Затем эти строки можно удалить.
#api_id = 12345
#api_hash = "0123456789abcdef0123456789abcdef"
#bot_token = "123456:ABc-DEF1234ghIkl-zyx57W2v1u123ew11"
#app = Client(nameclient, api_id=api_id, api_hash=api_hash, bot_token=bot_token)

#После удаления раскоментировать строку ниже.
app = Client(nameclient)


class PostObj: #объект поста из вк
    def __init__(self, posttext, urlbutton, attachdata=''):
        self.posttext = posttext
        self.urlbutton = urlbutton
        self.attachdata = attachdata

    def censor(self): #игнорирование постов по ключевым словам
        censorword = 0
        for word in ignore_words:
            if word.lower() in self.posttext.lower():
                censorword += 1
                self.posttext = self.posttext + '\n<s>' + word + '</s>'
                log.log(31, f'Обнаружено стоп слово: {word}')
        if censorword > 0:
            return False
        else:
            return True

    async def send_text_tg(self): #отправка объекта только с текстом в телеграм
        if PostObj.censor(self):
            uid = tgchatid
        else:
            log.log(31, 'Пост не прошёл цензуру.')
            uid = adminchat
        async with app:
            await app.send_message(uid, self.posttext, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Ссылка на пост', url=self.urlbutton)]]))

    async def send_text_photo_tg(self): #отправка объекта с текстом и фото в телеграм
        if PostObj.censor(self):
            uid = tgchatid
        else:
            log.log(31, 'Пост не прошёл цензуру.')
            uid = adminchat
        async with app:
            await app.send_photo(uid, self.attachdata, caption=self.posttext, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Ссылка на пост', url=self.urlbutton)]]))

    async def send_text_anim_tg(self): #отправка объекта с текстом и анимацией в телеграм
        if PostObj.censor(self):
            uid = tgchatid
        else:
            log.log(31, 'Пост не прошёл цензуру.')
            uid = adminchat
        async with app:
            await app.send_animation(adminchat, self.attachdata, caption=self.posttext, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Ссылка на пост', url=self.urlbutton)]]))


def readfiledate(): #чтение файла с датой последнего поста
    if os.path.isfile(DATESAVE):
        with open(DATESAVE, 'r', encoding='UTF-8') as f:
            return int(f.read())
    else:
        return int(time.time() - timeout)

def writefiledate(date): #запись файла с датой последнего поста
    with open(DATESAVE, 'w', encoding='UTF-8') as f:
            f.write(str(date + 1))

def crop_text(text): #обрезает длинный текст поста (более 800 символов)
    if len(text) > 800:
        return text[0:800] + '...'
    else:
        return text

def ask_vk():
    try:
        r = requests.get(URL).json()['response']
    except requests.exceptions.RequestException as e:
        log.exception(e)
    else:
        if r['items'] != []:
            groupsid = {}
            for g in range(len(r['groups'])): #получение имени группы
                groupsid[r['groups'][g]['id']] = r['groups'][g]['name']
            readtime = readfiledate()
            for s in range(len(r['items'])):
                if r['items'][s]['marked_as_ads'] == 1: #проверка рекламного поста
                    pass
                else:
                    try:
                        if r['items'][s]['copy_history']: #проверка на репост
                            pass
                    except:
                        postdate = r['items'][s]['date'] #время появления поста в unix. int
                        if postdate > readtime:
                            sourceid = r['items'][s]['source_id'] #источник поста. int со знаком - вначале
                            sourcename = '<u>' + groupsid[-sourceid] + '</u>' #имя группы. str
                            posttext = sourcename + '\n' + crop_text(r['items'][s]['text']) #текст поста. str
                            postid = r['items'][s]['post_id'] #id поста. int
                            urlbutton = f'https://vk.com/feed?w=wall{sourceid}_{postid}' #ссылка на пост вк для кнопки. str
                            attach = r['items'][s]['attachments'] #прикреплённые данные
                            if attach == []:
                                postobj = PostObj(posttext, urlbutton)
                                app.run(postobj.send_text_tg())
                            else:
                                if attach[0]['type'] == 'photo': #если тип фото
                                    urlphoto = ''
                                    for p in attach[0]['photo']['sizes']:
                                        if p['type'] == 'z':
                                            urlphoto = p['url']
                                            break
                                        elif p['type'] == 'y':
                                            urlphoto = p['url']
                                            break
                                        elif p['type'] == 'x':
                                            urlphoto = p['url']
                                            break
                                        else:
                                            urlphoto = errorphoto
                                    postobj = PostObj(posttext, urlbutton, urlphoto)
                                    log.log(31, 'Пост с текстом и фотографией отправлен в telegram.')
                                    app.run(postobj.send_text_photo_tg())
                                elif attach[0]['type'] == 'video': #если тип видео
                                    idvideo = attach[0]['video']['id']
                                    ownervideo = attach[0]['video']['owner_id']
                                    posttext = f'{posttext}\nhttps://vk.com/video{ownervideo}_{idvideo}'
                                    postobj = PostObj(posttext, urlbutton) #объект поста с текстом и ссылкой на видео
                                    log.log(31, 'Пост с текстом и видео отправлен в telegram.')
                                    app.run(postobj.send_text_tg()) #объект поста отправляется в телеграм
                                elif attach[0]['type'] == 'link': #если тип ссылка
                                    urllink = attach[0]['link']['url']
                                    posttext = re.sub(r'http\S+', '', posttext)
                                    posttext = f'{posttext}\n{urllink}'
                                    postobj = PostObj(posttext, urlbutton) #объект поста с текстом и ссылкой
                                    log.log(31, 'Пост с текстом и ссылкой отправлен в telegram.')
                                    app.run(postobj.send_text_tg()) #объект поста отправляется в телеграм
                                elif attach[0]['type'] == 'audio': #если тип аудио
                                    posttext = f'{posttext}\n<i>Есть наличие аудиофайлов</i>'
                                    postobj = PostObj(posttext, urlbutton) #объект поста с текстом и аудио
                                    log.log(31, 'Пост с текстом и аудио отправлен в telegram.')
                                    app.run(postobj.send_text_tg()) #объект поста отправляется в телеграм
                                elif attach[0]['type'] == 'poll': #если тип опрос
                                    question = attach[0]['poll']['question']
                                    posttext = f'{posttext}\n<i>К посту прикреплён опрос:</i>\n{question}'
                                    postobj = PostObj(posttext, urlbutton) #объект поста с текстом и опросом
                                    log.log(31, 'Пост с текстом и опросом отправлен в telegram.')
                                    app.run(postobj.send_text_tg()) #объект поста отправляется в телеграм
                                elif attach[0]['type'] == 'doc': #если тип файл
                                    exttype = attach[0]['doc']['ext']
                                    urldoc = attach[0]['doc']['url']
                                    if exttype == 'jpg':
                                        postobj = PostObj(posttext, urlbutton, urldoc) #объект поста с текстом и фото
                                        log.log(31, 'Пост с текстом и фотодокументом отправлен в telegram.')
                                        app.run(postobj.send_text_photo_tg()) #объект поста отправляется в телеграм
                                    elif exttype == 'gif':
                                        postobj = PostObj(posttext, urlbutton, urldoc) #объект поста с текстом и гифкой
                                        log.log(31, 'Пост с текстом и гифкой отправлен в telegram.')
                                        app.run(postobj.send_text_anim_tg()) #объект поста отправляется в телеграм
                                    elif exttype == 'doc':
                                        posttext = f'{posttext}\n{urldoc}'
                                        postobj = PostObj(posttext, urlbutton) #объект поста с текстом и документом
                                        log.log(31, 'Пост с текстом и документом отправлен в telegram.')
                                        app.run(postobj.send_text_tg()) #объект поста отправляется в телеграм
                                    else:
                                        postobj = PostObj(posttext, urlbutton) #объект поста с текстом и документом
                                        log.log(31, 'Пост с текстом и файлом отправлен в telegram.')
                                        app.run(postobj.send_text_tg()) #объект поста отправляется в телеграм
                                else:
                                    postobj = PostObj(posttext, urlbutton) #объект поста с текстом и документом
                                    log.log(31, 'Пост с текстом отправлен в telegram.')
                                    app.run(postobj.send_text_tg()) #объект поста отправляется в телеграм
                        else:
                            pass

            if r['items'][0]['date'] > readtime:
                writefiledate(r['items'][0]['date']) #записываем время свежего поста в datesave файл
            else:
                pass
        else:
            log.log(31, 'Пришёл пустой запрос от Вконтакте.')
            pass

def main():
    log.log(31, '***Запуск бота***')
    while True:
        ask_vk()
        try:
            time.sleep(timeout)
        except KeyboardInterrupt:
            log.log(31, '***Остановка бота***')
            break

if __name__ == '__main__':
    main()
