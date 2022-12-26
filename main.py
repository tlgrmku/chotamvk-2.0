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
FORMAT = '%(asctime)s %(levelname)s %(message)s'
logging.basicConfig(level=logging.INFO, filename=LOGF, format=FORMAT)

log = logging.getLogger()
app = Client(nameclient)


class PostObj: #объект поста из вк
    def __init__(self, posttext, urlbutton, attachdata=''):
        self.posttext = posttext #текст поста с названием группы
        self.urlbutton = urlbutton #ссылка на пост вк для кнопки
        self.attachdata = attachdata #прикреплённые файлы поста


    def censor(self): #игнорирование постов по ключевым словам
        w = 0
        for word in ignore_words:
            if word.lower() in self.posttext.lower():
                w += 1
                self.posttext = self.posttext + '\n<s>' + word + '</s>'
                log.info(f'*** Обнаружено стоп слово: {word}')
        if w > 0:
            return False
        else:
            return True


    def send_text_tg(self): #отправка объекта только с текстом в телеграм
        if PostObj.censor(self):
            log.info('*** Пост с текстом отправлен в telegram')
            with app:
                app.send_message(tgchatid, self.posttext, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Ссылка на пост', url=self.urlbutton)]]))
            time.sleep(5) #задержка что бы телеграм не ругался:)
        else:
            log.info('*** Пост не прошёл цензуру.')
            with app:
                app.send_message(adminchat, self.posttext, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Ссылка на пост', url=self.urlbutton)]]))
            time.sleep(5) #задержка что бы телеграм не ругался:)


    def send_text_photo_tg(self): #отправка объекта с текстом и фото в телеграм
        if PostObj.censor(self):
            log.info('*** Пост с текстом и фото отправлен в telegram')
            with app:
                app.send_photo(tgchatid, self.attachdata, caption=self.posttext, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Ссылка на пост', url=self.urlbutton)]]))
            time.sleep(5) #задержка что бы телеграм не ругался:)
        else:
            log.info('*** Пост не прошёл цензуру.')
            with app:
                app.send_photo(adminchat, self.attachdata, caption=self.posttext, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Ссылка на пост', url=self.urlbutton)]]))
            time.sleep(5) #задержка что бы телеграм не ругался:)


    def send_text_anim_tg(self): #отправка объекта с текстом и анимацией в телеграм
        if PostObj.censor(self):
            log.info('*** Пост с текстом и анимацией отправлен в telegram')
            with app:
                app.send_animation(tgchatid, self.attachdata, caption=self.posttext, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Ссылка на пост', url=self.urlbutton)]]))
            time.sleep(5) #задержка что бы телеграм не ругался:)
        else:
            log.info('*** Пост не прошёл цензуру.')
            with app:
                app.send_animation(adminchat, self.attachdata, caption=self.posttext, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Ссылка на пост', url=self.urlbutton)]]))
            time.sleep(5) #задержка что бы телеграм не ругался:)


def rfiledate(): #чтение файла с датой последнего поста
    if os.path.isfile(DATESAVE):
        with open(DATESAVE, 'r', encoding='UTF-8') as f:
            return int(f.read())
    else:
        return int(time.time() - timeout)


def wfiledate(date): #запись файла с датой последнего поста
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
    except requests.ConnectionError as e:
        log.exception(e)
    else:
        if r['items'] != []:
            groupsid = {}
            for g in range(len(r['groups'])): #получение имени группы
                groupsid[r['groups'][g]['id']] = r['groups'][g]['name']
            readtime = rfiledate()
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
                            try:
                                attach = r['items'][s]['attachments'] #прикреплённые данные
                            except:
                                postobj = PostObj(posttext, urlbutton)
                                postobj.send_text_tg()
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
                                    postobj.send_text_photo_tg()
                                elif attach[0]['type'] == 'video': #если тип видео
                                    idvideo = attach[0]['video']['id']
                                    ownervideo = attach[0]['video']['owner_id']
                                    posttext = f'{posttext}\nhttps://vk.com/video{ownervideo}_{idvideo}'
                                    postobj = PostObj(posttext, urlbutton) #объект поста с текстом и ссылкой на видео
                                    postobj.send_text_tg() #объект поста отправляется в телеграм
                                elif attach[0]['type'] == 'link': #если тип ссылка
                                    urllink = attach[0]['link']['url']
                                    posttext = re.sub(r'http\S+', '', posttext)
                                    posttext = f'{posttext}\n{urllink}'
                                    postobj = PostObj(posttext, urlbutton) #объект поста с текстом и ссылкой
                                    postobj.send_text_tg() #объект поста отправляется в телеграм
                                elif attach[0]['type'] == 'audio': #если тип аудио
                                    posttext = f'{posttext}\n<i>Есть наличие аудиофайлов</i>'
                                    postobj = PostObj(posttext, urlbutton) #объект поста с текстом и аудио
                                    postobj.send_text_tg() #объект поста отправляется в телеграм
                                elif attach[0]['type'] == 'poll': #если тип опрос
                                    question = attach[0]['poll']['question']
                                    posttext = f'{posttext}\n<i>К посту прикреплён опрос:</i>\n{question}'
                                    postobj = PostObj(posttext, urlbutton) #объект поста с текстом и опросом
                                    postobj.send_text_tg() #объект поста отправляется в телеграм
                                elif attach[0]['type'] == 'doc': #если тип файл
                                    exttype = attach[0]['doc']['ext']
                                    urldoc = attach[0]['doc']['url']
                                    if exttype == 'jpg':
                                        postobj = PostObj(posttext, urlbutton, urldoc) #объект поста с текстом и фото
                                        postobj.send_text_photo_tg() #объект поста отправляется в телеграм
                                    elif exttype == 'gif':
                                        postobj = PostObj(posttext, urlbutton, urldoc) #объект поста с текстом и гифкой
                                        postobj.send_text_anim_tg() #объект поста отправляется в телеграм
                                    elif exttype == 'doc':
                                        posttext = f'{posttext}\n{urldoc}'
                                        postobj = PostObj(posttext, urlbutton) #объект поста с текстом и документом
                                        postobj.send_text_tg() #объект поста отправляется в телеграм
                                    else:
                                        postobj = PostObj(posttext, urlbutton) #объект поста с текстом и документом
                                        postobj.send_text_tg() #объект поста отправляется в телеграм
                                else:
                                    postobj = PostObj(posttext, urlbutton) #объект поста с текстом и документом
                                    postobj.send_text_tg() #объект поста отправляется в телеграм
                        else:
                            pass
            if r['items'][0]['date'] > readtime:
                wfiledate(r['items'][0]['date']) #записываем время свежего поста в datesave файл
            else:
                pass
        else:
            pass


def main():
    while True:
        ask_vk()
        try:
            time.sleep(timeout)
        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    main()
