#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram
import requests
import logging
import mysql.connector
from mysql.connector import Error
import re
import urllib
import time

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    replymarkup = telegram.ReplyKeyboardMarkup([[telegram.KeyboardButton('Город'), telegram.KeyboardButton('Край'),
                                                 telegram.KeyboardButton('Происшествия'),
                                                 telegram.KeyboardButton('Культура'),
                                                 telegram.KeyboardButton('Спорт'),
                                                 telegram.KeyboardButton('Все')]], resize_keyboard=True,
                                               one_time_keyboard=True)
    url = u'Бот сайта komcity.ru приветствует вас!' + u'\n' + u'Вы можете подписаться на определенные категории новостей, нажав соответствующие кнопки' + u'\n' + u'или ввести команды:' + u'\n' + u'Город или /city - новости города,' + u'\n' + u'Край или /region - новости края,' + u'\n' + u'Происшествия или /accident - новости о происшествиях,' + u'\n' + u'Культура или /culture - новости культуры,' + u'\n' + u'Спорт или /sport - новости спорта,' + u'\n' + u'Все или /all - все категории. Так же выводит категории, на которые есть подписка' + u'\n' + u'/pogoda или /погода - узнать текущую погоду.' + u'\n' + u'Чтобы отписаться от категории введите ее название еще раз.' + u'\n'
    url=url.encode('UTF-8')
    bot.sendMessage(update.message.chat_id, text=url, reply_markup=replymarkup)

def help(bot, update):
    replymarkup = telegram.ReplyKeyboardMarkup([[telegram.KeyboardButton('Город'), telegram.KeyboardButton('Край'),
                                                 telegram.KeyboardButton('Происшествия'),
                                                 telegram.KeyboardButton('Культура'),
                                                 telegram.KeyboardButton('Спорт'),
                                                 telegram.KeyboardButton('Все')]], resize_keyboard=True,
                                               one_time_keyboard=True)
    url = u'Бот сайта komcity.ru приветствует вас!' + u'\n' + u'Вы можете подписаться на определенные категории новостей, нажав соответствующие кнопки' + u'\n' + u'или ввести команды:' + u'\n' + u'Город или /city - новости города,' + u'\n' + u'Край или /region - новости края,' + u'\n' + u'Происшествия или /accident - новости о происшествиях,' + u'\n' + u'Культура или /culture - новости культуры,' + u'\n' + u'Спорт или /sport - новости спорта,' + u'\n' + u'Все или /all - все категории. Так же выводит категории, на которые есть подписка' + u'\n' + u'/pogoda или /погода - узнать текущую погоду.' + u'\n' + u'Чтобы отписаться от категории введите ее название еще раз.' + u'\n'
    url=url.encode('UTF-8')
    bot.sendMessage(update.message.chat_id, text=url, reply_markup=replymarkup)

# def echo(bot, update):
#    bot.sendMessage(update.message.chat_id, text=update.message.text)

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def weather(bot, update):
    weatherurl = 'http://www.'
    weatherresponse = requests.get(weatherurl)
    weatherjson = weatherresponse.json()
    phantomtemp = weatherjson['outdoortemp']
    if weatherjson['outdoortemp'] == weatherjson['heatindex']:
        phantomtemp = weatherjson['windchill']
    else:
        phantomtemp = weatherjson['heatindex']
    msg = u'Текущая погода:' + u'\n'
    msg = msg + u"Температура воздуха: " + weatherjson['outdoortemp'] + u" °C" + u"\n"
    msg = msg + u"Ощущаемая температура: " + phantomtemp + u" °C" + u"\n"
    msg = msg + u"Ветер: " + weatherjson['windrosedirection'] + " " + weatherjson['windspeed'] + u" м/c" + u"\n"
    msg = msg + u"Относительная влажность воздуха: " + weatherjson['hum'] + u"%" + u"\n"
    msg = msg + u"Атмосферное давление: " + weatherjson['baropressure'] + u" мм.рт.ст. " + weatherjson[
        'barotrend'] + u"\n"
    msg = msg + u"\n"
    msg = msg + u'Прогноз: ' + "\n" + weatherjson['frule'] + u"\n"
    bot.sendMessage(update.message.chat_id, text=msg.encode('UTF-8'))

def textshorter(text):
    end = '...'
    result = text.decode('UTF-8')
    #result = text
    if len(result) > 150:
        result = result[:150] + end
    else:
        result = result
    return (result)

#options for keyboard
def news(bot, update):
    i=0
    replytxt = update.message.text
    chatid = update.message.chat_id
    userid = update.message.from_user.id
    chat_type = bot.get_chat(chatid)
    conn = mysql.connector.connect(host='', database='', user='', password='')
    if chat_type.type != "private":
        admin = bot.get_chat_administrators(chatid)
        for user_id in admin:
            if user_id.user.id != userid:
                i = i
            else:
                i = i + 1
        if i == 0:
            bot.sendMessage(update.message.chat_id, text=u"Вы не являетесь администратором группы и не можете настраивать бота!")
        else:
            if replytxt == u'Город' or replytxt == u'город':
                try:
                    cursor = conn.cursor(buffered=True)
                    qselect = "SELECT TelegramUserid FROM TelegramSubscribe WHERE NewsCategory=1 AND TelegramUserid = '%s'"
                    cursor.execute(qselect, (chatid,))
                    if cursor.rowcount != 0:
                        bot.sendMessage(update.message.chat_id,
                                        text=u"Вы уже подписаны на категорию Город. Удаляю подписку.")
                        qdelete = "DELETE FROM TelegramSubscribe WHERE TelegramUserid='%s' AND NewsCategory=1"
                        cursor.execute(qdelete, (chatid,))
                        conn.commit()
                    else:
                        qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                        cursor.execute(qinsert, (chatid, 1))
                        conn.commit()
                        bot.sendMessage(update.message.chat_id, text=u"Вы подписались на новости в категории Город")
                except Error as e:
                    print(e)
                finally:
                    cursor.close()
                    conn.close()
            elif replytxt == u'Край' or replytxt == u'край':
                try:
                    cursor = conn.cursor(buffered=True)
                    qselect = "SELECT TelegramUserid FROM TelegramSubscribe WHERE NewsCategory=2 AND TelegramUserid = '%s'"
                    cursor.execute(qselect, (chatid,))
                    if cursor.rowcount != 0:
                        bot.sendMessage(update.message.chat_id,
                                        text=u"Вы уже подписаны на категорию Край. Удаляю подписку.")
                        qdelete = "DELETE FROM TelegramSubscribe WHERE TelegramUserid='%s' AND NewsCategory=2"
                        cursor.execute(qdelete, (chatid,))
                        conn.commit()
                    else:
                        qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                        cursor.execute(qinsert, (chatid, 2))
                        conn.commit()
                        bot.sendMessage(update.message.chat_id, text=u"Вы подписались на новости в категории Край")
                except Error as e:
                    print(e)
                finally:
                    cursor.close()
                    conn.close()
            elif replytxt == u'Происшествия' or replytxt == u'происшествия':
                try:
                    cursor = conn.cursor(buffered=True)
                    qselect = "SELECT TelegramUserid FROM TelegramSubscribe WHERE NewsCategory=3 AND TelegramUserid = '%s'"
                    cursor.execute(qselect, (chatid,))
                    if cursor.rowcount != 0:
                        bot.sendMessage(update.message.chat_id,
                                        text=u"Вы уже подписаны на категорию Происшествия. Удаляю подписку.")
                        qdelete = "DELETE FROM TelegramSubscribe WHERE TelegramUserid='%s' AND NewsCategory=3"
                        cursor.execute(qdelete, (chatid,))
                        conn.commit()
                    else:
                        qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                        cursor.execute(qinsert, (chatid, 3))
                        conn.commit()
                        bot.sendMessage(update.message.chat_id,
                                        text=u"Вы подписались на новости в категории Происшествия")
                except Error as e:
                    print(e)
                finally:
                    cursor.close()
                    conn.close()
            elif replytxt == u'Культура' or replytxt == u'культура':
                try:
                    cursor = conn.cursor(buffered=True)
                    qselect = "SELECT TelegramUserid FROM TelegramSubscribe WHERE NewsCategory=4 AND TelegramUserid = '%s'"
                    cursor.execute(qselect, (chatid,))
                    if cursor.rowcount != 0:
                        bot.sendMessage(update.message.chat_id,
                                        text=u"Вы уже подписаны на категорию Культура. Удаляю подписку.")
                        qdelete = "DELETE FROM TelegramSubscribe WHERE TelegramUserid='%s' AND NewsCategory=4"
                        cursor.execute(qdelete, (chatid,))
                        conn.commit()
                    else:
                        qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                        cursor.execute(qinsert, (chatid, 4))
                        conn.commit()
                        bot.sendMessage(update.message.chat_id,
                                        text=u"Вы подписались на новости в категории Культура.")
                except Error as e:
                    print(e)
                finally:
                    cursor.close()
                    conn.close()
            elif replytxt == u'Спорт' or replytxt == u'спорт':
                try:
                    cursor = conn.cursor(buffered=True)
                    qselect = "SELECT TelegramUserid FROM TelegramSubscribe WHERE NewsCategory=5 AND TelegramUserid = '%s'"
                    cursor.execute(qselect, (chatid,))
                    if cursor.rowcount != 0:
                        bot.sendMessage(update.message.chat_id,
                                        text=u"Вы уже подписаны на категорию Спорт. Удаляю подписку.")
                        qdelete = "DELETE FROM TelegramSubscribe WHERE TelegramUserid='%s' AND NewsCategory=4"
                        cursor.execute(qdelete, (chatid,))
                        conn.commit()
                    else:
                        qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                        cursor.execute(qinsert, (chatid, 5))
                        conn.commit()
                        bot.sendMessage(update.message.chat_id, text=u"Вы подписались на новости в категории Спорт.")
                except Error as e:
                    print(e)
                finally:
                    cursor.close()
                    conn.close()
            elif replytxt == u'Все' or replytxt == u'все':
                try:
                    cursor = conn.cursor(buffered=True)
                    qselect = "SELECT TelegramUserId, NewsCategoryTxt FROM TelegramSubscribe INNER JOIN NewsCategory WHERE TelegramSubscribe.NewsCategory=NewsCategory.NewsCategoryId AND TelegramSubscribe.TelegramUserId='%s' ORDER BY NewsCategoryTxt ASC"
                    cursor.execute(qselect, (chatid,))
                    if cursor.rowcount != 0:
                        txt = u'Вы уже подписаны на категорию:' + u'\n'
                        row = cursor.fetchone()
                        while row is not None:
                            txt = txt + row[1] + u'\n'
                            row = cursor.fetchone()
                        txt = txt + u'Чтобы удалить или добавить категорию, используйте отдельные команды.'
                        bot.sendMessage(update.message.chat_id, text=txt)
                    else:
                        for x in range(1, 6):
                            qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                            cursor.execute(qinsert, (chatid, x))
                            conn.commit()
                        bot.sendMessage(update.message.chat_id, text=u"Вы подписались на все категории новостей.")
                except Error as e:
                    print(e)
                finally:
                    cursor.close()
                    conn.close()
            else:
                bot.sendMessage(update.message.chat_id, text=u'Неверная команда. Наберите /help или /помощь')
    else:
        if replytxt == u'Город' or replytxt == u'город':
            try:
                cursor = conn.cursor(buffered=True)
                qselect = "SELECT TelegramUserid FROM TelegramSubscribe WHERE NewsCategory=1 AND TelegramUserid = '%s'"
                cursor.execute(qselect, (chatid,))
                if cursor.rowcount != 0:
                    bot.sendMessage(update.message.chat_id,
                                    text=u"Вы уже подписаны на категорию Город. Удаляю подписку.")
                    qdelete = "DELETE FROM TelegramSubscribe WHERE TelegramUserid='%s' AND NewsCategory=1"
                    cursor.execute(qdelete, (chatid,))
                    conn.commit()
                else:
                    qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                    cursor.execute(qinsert, (chatid, 1))
                    conn.commit()
                    bot.sendMessage(update.message.chat_id, text=u"Вы подписались на новости в категории Город")
            except Error as e:
                print(e)
            finally:
                cursor.close()
                conn.close()
        elif replytxt == u'Край' or replytxt == u'край':
            try:
                cursor = conn.cursor(buffered=True)
                qselect = "SELECT TelegramUserid FROM TelegramSubscribe WHERE NewsCategory=2 AND TelegramUserid = '%s'"
                cursor.execute(qselect, (chatid,))
                if cursor.rowcount != 0:
                    bot.sendMessage(update.message.chat_id, text=u"Вы уже подписаны на категорию Край. Удаляю подписку.")
                    qdelete = "DELETE FROM TelegramSubscribe WHERE TelegramUserid='%s' AND NewsCategory=2"
                    cursor.execute(qdelete, (chatid,))
                    conn.commit()
                else:
                    qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                    cursor.execute(qinsert, (chatid, 2))
                    conn.commit()
                    bot.sendMessage(update.message.chat_id, text=u"Вы подписались на новости в категории Край.")
            except Error as e:
                print(e)
            finally:
                cursor.close()
                conn.close()
        elif replytxt == u'Происшествия' or replytxt == u'происшествия':
            try:
                cursor = conn.cursor(buffered=True)
                qselect = "SELECT TelegramUserid FROM TelegramSubscribe WHERE NewsCategory=3 AND TelegramUserid = '%s'"
                cursor.execute(qselect, (chatid,))
                if cursor.rowcount != 0:
                    bot.sendMessage(update.message.chat_id,
                                    text=u"Вы уже подписаны на категорию Происшествия. Удаляю подписку.")
                    qdelete = "DELETE FROM TelegramSubscribe WHERE TelegramUserid='%s' AND NewsCategory=3"
                    cursor.execute(qdelete, (chatid,))
                    conn.commit()
                else:
                    qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                    cursor.execute(qinsert, (chatid, 3))
                    conn.commit()
                    bot.sendMessage(update.message.chat_id, text=u"Вы подписались на новости в категории Происшествия.")
            except Error as e:
                print(e)
            finally:
                cursor.close()
                conn.close()
        elif replytxt == u'Культура' or replytxt == u'культура':
            try:
                cursor = conn.cursor(buffered=True)
                qselect = "SELECT TelegramUserid FROM TelegramSubscribe WHERE NewsCategory=4 AND TelegramUserid = '%s'"
                cursor.execute(qselect, (chatid,))
                if cursor.rowcount != 0:
                    bot.sendMessage(update.message.chat_id,
                                    text=u"Вы уже подписаны на категорию Культура. Удаляю подписку.")
                    qdelete = "DELETE FROM TelegramSubscribe WHERE TelegramUserid='%s' AND NewsCategory=4"
                    cursor.execute(qdelete, (chatid,))
                    conn.commit()
                else:
                    qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                    cursor.execute(qinsert, (chatid, 4))
                    conn.commit()
                    bot.sendMessage(update.message.chat_id, text=u"Вы подписались на новости в категории Культура.")
            except Error as e:
                print(e)
            finally:
                cursor.close()
                conn.close()
        elif replytxt == u'Спорт' or replytxt == u'спорт':
            try:
                cursor = conn.cursor(buffered=True)
                qselect = "SELECT TelegramUserid FROM TelegramSubscribe WHERE NewsCategory=5 AND TelegramUserid = '%s'"
                cursor.execute(qselect, (chatid,))
                if cursor.rowcount != 0:
                    bot.sendMessage(update.message.chat_id,
                                    text=u"Вы уже подписаны на категорию Спорт. Удаляю подписку.")
                    qdelete = "DELETE FROM TelegramSubscribe WHERE TelegramUserid='%s' AND NewsCategory=5"
                    cursor.execute(qdelete, (chatid,))
                    conn.commit()
                else:
                    qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                    cursor.execute(qinsert, (chatid, 5))
                    conn.commit()
                    bot.sendMessage(update.message.chat_id, text=u"Вы подписались на новости в категории Спорт.")
            except Error as e:
                print(e)
            finally:
                cursor.close()
                conn.close()
        elif replytxt == u'Все' or replytxt == u'все':
            try:
                cursor = conn.cursor(buffered=True)
                qselect = "SELECT TelegramUserId, NewsCategoryTxt FROM TelegramSubscribe INNER JOIN NewsCategory WHERE TelegramSubscribe.NewsCategory=NewsCategory.NewsCategoryId AND TelegramSubscribe.TelegramUserId='%s' ORDER BY NewsCategoryTxt ASC"
                cursor.execute(qselect, (chatid,))
                if cursor.rowcount != 0:
                    txt = u'Вы уже подписаны на категорию:' + u'\n'
                    row = cursor.fetchone()
                    while row is not None:
                        txt = txt + row[1] + u'\n'
                        row = cursor.fetchone()
                    txt = txt + u'Чтобы удалить или добавить категорию, используйте отдельные команды.'
                    bot.sendMessage(update.message.chat_id, text=txt)
                else:
                    for x in range(1, 6):
                        qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                        cursor.execute(qinsert, (chatid, x))
                        conn.commit()
                    bot.sendMessage(update.message.chat_id, text=u"Вы подписались на все категории новостей.")
            except Error as e:
                print(e)
            finally:
                cursor.close()
                conn.close()
        else:
            bot.sendMessage(update.message.chat_id, text=u'Неверная команда. Наберите /help или /помощь')

# подписка и отписка от новостей в категории город
def ncity(bot, update):
    i=0
    chatid = update.message.chat_id
    userid = update.message.from_user.id
    chat_type = bot.get_chat(chatid)
    conn = mysql.connector.connect(host='', database='', user='', password='')
    if chat_type.type != "private":
        admin = bot.get_chat_administrators(chatid)
        for user_id in admin:
            if user_id.user.id != userid:
                i = i
            else:
                i = i + 1
        if i == 0:
            bot.sendMessage(update.message.chat_id, text=u"Вы не являетесь администратором группы и не можете настраивать бота!")
        else:
            try:
                cursor = conn.cursor(buffered=True)
                qselect = "SELECT TelegramUserid FROM TelegramSubscribe WHERE NewsCategory=1 AND TelegramUserid = '%s'"
                cursor.execute(qselect, (chatid,))
                if cursor.rowcount != 0:
                    bot.sendMessage(update.message.chat_id,
                                    text=u"Вы уже подписаны на категорию Город. Удаляю подписку.")
                    qdelete = "DELETE FROM TelegramSubscribe WHERE TelegramUserid='%s' AND NewsCategory=1"
                    cursor.execute(qdelete, (chatid,))
                    conn.commit()
                else:
                    qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                    cursor.execute(qinsert, (chatid, 1))
                    conn.commit()
                    bot.sendMessage(update.message.chat_id, text=u"Вы подписались на новости в категории Город")
            except Error as e:
                print(e)
            finally:
                cursor.close()
                conn.close()
    else:
        try:
            cursor = conn.cursor(buffered=True)
            qselect = "SELECT TelegramUserid FROM TelegramSubscribe WHERE NewsCategory=1 AND TelegramUserid = '%s'"
            cursor.execute(qselect, (chatid,))
            if cursor.rowcount != 0:
                qdelete = "DELETE FROM TelegramSubscribe WHERE TelegramUserid='%s' AND NewsCategory=1"
                cursor.execute(qdelete, (chatid,))
                conn.commit()
                bot.sendMessage(update.message.chat_id, text=u"Вы уже подписаны на категорию Город. Удаляю подписку.")
            else:
                qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                cursor.execute(qinsert, (chatid, 1))
                conn.commit()
                bot.sendMessage(update.message.chat_id, text=u"Вы подписались на новости в категории Город")
        except Error as e:
            print(e)
        finally:
            cursor.close()
            conn.close()

# подписка и отписка от новостей в категории край
def nregion(bot, update):
    i=0
    chatid = update.message.chat_id
    userid = update.message.from_user.id
    chat_type = bot.get_chat(chatid)
    conn = mysql.connector.connect(host='', database='', user='', password='')
    if chat_type.type != "private":
        admin = bot.get_chat_administrators(chatid)
        for user_id in admin:
            if user_id.user.id != userid:
                i = i
            else:
                i = i + 1
        if i == 0:
            bot.sendMessage(update.message.chat_id, text=u"Вы не являетесь администратором группы и не можете настраивать бота!")
        else:
            try:
                cursor = conn.cursor(buffered=True)
                qselect = "SELECT TelegramUserid FROM TelegramSubscribe WHERE NewsCategory=2 AND TelegramUserid = '%s'"
                cursor.execute(qselect, (chatid,))
                if cursor.rowcount != 0:
                    bot.sendMessage(update.message.chat_id,
                                    text=u"Вы уже подписаны на категорию Край. Удаляю подписку.")
                    qdelete = "DELETE FROM TelegramSubscribe WHERE TelegramUserid='%s' AND NewsCategory=2"
                    cursor.execute(qdelete, (chatid,))
                    conn.commit()
                else:
                    qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                    cursor.execute(qinsert, (chatid, 2))
                    conn.commit()
                    bot.sendMessage(update.message.chat_id, text=u"Вы подписались на новости в категории Край.")
            except Error as e:
                print(e)
            finally:
                cursor.close()
                conn.close()
    else:
        try:
            cursor = conn.cursor(buffered=True)
            qselect = "SELECT TelegramUserid FROM TelegramSubscribe WHERE NewsCategory=2 AND TelegramUserid = '%s'"
            cursor.execute(qselect, (chatid,))
            if cursor.rowcount != 0:
                qdelete = "DELETE FROM TelegramSubscribe WHERE TelegramUserid='%s' AND NewsCategory=2"
                cursor.execute(qdelete, (chatid,))
                conn.commit()
                bot.sendMessage(update.message.chat_id, text=u"Вы уже подписаны на категорию Край. Удаляю подписку.")
            else:
                qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                cursor.execute(qinsert, (chatid, 2))
                conn.commit()
                bot.sendMessage(update.message.chat_id, text=u"Вы подписались на новости в категории Край.")
        except Error as e:
            print(e)
        finally:
            cursor.close()
            conn.close()

# подписка и отписка на новости в категории происшествия
def naccident(bot, update):
    i=0
    chatid = update.message.chat_id
    userid = update.message.from_user.id
    chat_type = bot.get_chat(chatid)
    conn = mysql.connector.connect(host='', database='', user='', password='')
    if chat_type.type != "private":
        admin = bot.get_chat_administrators(chatid)
        for user_id in admin:
            if user_id.user.id != userid:
                i = i
            else:
                i = i + 1
        if i == 0:
            bot.sendMessage(update.message.chat_id, text=u"Вы не являетесь администратором группы и не можете настраивать бота!")
        else:
            try:
                cursor = conn.cursor(buffered=True)
                qselect = "SELECT TelegramUserid FROM TelegramSubscribe WHERE NewsCategory=3 AND TelegramUserid = '%s'"
                cursor.execute(qselect, (chatid,))
                if cursor.rowcount != 0:
                    bot.sendMessage(update.message.chat_id,
                                    text=u"Вы уже подписаны на категорию Происшествия. Удаляю подписку.")
                    qdelete = "DELETE FROM TelegramSubscribe WHERE TelegramUserid='%s' AND NewsCategory=3"
                    cursor.execute(qdelete, (chatid,))
                    conn.commit()
                else:
                    qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                    cursor.execute(qinsert, (chatid, 3))
                    conn.commit()
                    bot.sendMessage(update.message.chat_id,
                                    text=u"Вы подписались на новости в категории Происшествия.")
            except Error as e:
                print(e)
            finally:
                cursor.close()
                conn.close()
    else:
        try:
            cursor = conn.cursor(buffered=True)
            qselect = "SELECT TelegramUserid FROM TelegramSubscribe WHERE NewsCategory=3 AND TelegramUserid = '%s'"
            cursor.execute(qselect, (chatid,))
            if cursor.rowcount != 0:
                qdelete = "DELETE FROM TelegramSubscribe WHERE TelegramUserid='%s' AND NewsCategory=3"
                cursor.execute(qdelete, (chatid,))
                conn.commit()
                bot.sendMessage(update.message.chat_id,
                                text=u"Вы уже подписаны на категорию Происшествия. Удаляю подписку.")
            else:
                qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                cursor.execute(qinsert, (chatid, 3))
                conn.commit()
                bot.sendMessage(update.message.chat_id, text=u"Вы подписались на новости в категории Происшествия.")
        except Error as e:
            print(e)
        finally:
            cursor.close()
            conn.close()

# подписка и отписка от новости в категории культура
def nculture(bot, update):
    i=0
    chatid = update.message.chat_id
    userid = update.message.from_user.id
    chat_type = bot.get_chat(chatid)
    conn = mysql.connector.connect(host='', database='', user='', password='')
    if chat_type.type != "private":
        admin = bot.get_chat_administrators(chatid)
        for user_id in admin:
            if user_id.user.id != userid:
                i = i
            else:
                i = i + 1
        if i == 0:
            bot.sendMessage(update.message.chat_id, text=u"Вы не являетесь администратором группы и не можете настраивать бота!")
        else:
            try:
                cursor = conn.cursor(buffered=True)
                qselect = "SELECT TelegramUserid FROM TelegramSubscribe WHERE NewsCategory=4 AND TelegramUserid = '%s'"
                cursor.execute(qselect, (chatid,))
                if cursor.rowcount != 0:
                    bot.sendMessage(update.message.chat_id,
                                    text=u"Вы уже подписаны на категорию Культура. Удаляю подписку.")
                    qdelete = "DELETE FROM TelegramSubscribe WHERE TelegramUserid='%s' AND NewsCategory=4"
                    cursor.execute(qdelete, (chatid,))
                    conn.commit()
                else:
                    qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                    cursor.execute(qinsert, (chatid, 4))
                    conn.commit()
                    bot.sendMessage(update.message.chat_id, text=u"Вы подписались на новости в категории Культура.")
            except Error as e:
                print(e)
            finally:
                cursor.close()
                conn.close()
    else:
        try:
            cursor = conn.cursor(buffered=True)
            qselect = "SELECT TelegramUserid FROM TelegramSubscribe WHERE NewsCategory=4 AND TelegramUserid = '%s'"
            cursor.execute(qselect, (chatid,))
            if cursor.rowcount != 0:
                qdelete = "DELETE FROM TelegramSubscribe WHERE TelegramUserid='%s' AND NewsCategory=4"
                cursor.execute(qdelete, (chatid,))
                conn.commit()
                bot.sendMessage(update.message.chat_id, text=u"Вы уже подписаны на категорию Культура. Удаляю подписку.")
            else:
                qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                cursor.execute(qinsert, (chatid, 4))
                conn.commit()
                bot.sendMessage(update.message.chat_id, text=u"Вы подписались на новости в категории Культура.")
        except Error as e:
            print(e)
        finally:
            cursor.close()
            conn.close()

# подписка и отписка от новости в категории спорт
def nsport(bot, update):
    i=0
    chatid = update.message.chat_id
    userid = update.message.from_user.id
    chat_type = bot.get_chat(chatid)
    conn = mysql.connector.connect(host='', database='', user='', password='')
    if chat_type.type != "private":
        admin = bot.get_chat_administrators(chatid)
        for user_id in admin:
            if user_id.user.id != userid:
                i=i
            else:
                i=i+1
        if i==0:
            bot.sendMessage(update.message.chat_id,text=u"Вы не являетесь администратором группы и не можете настраивать бота!")
        else:
            try:
                cursor = conn.cursor(buffered=True)
                qselect = "SELECT TelegramUserid FROM TelegramSubscribe WHERE NewsCategory=5 AND TelegramUserid = '%s'"
                cursor.execute(qselect, (chatid,))
                if cursor.rowcount != 0:
                    bot.sendMessage(update.message.chat_id,
                                    text=u"Вы уже подписаны на категорию Спорт. Удаляю подписку.")
                    qdelete = "DELETE FROM TelegramSubscribe WHERE TelegramUserid='%s' AND NewsCategory=5"
                    cursor.execute(qdelete, (chatid,))
                    conn.commit()
                else:
                    qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                    cursor.execute(qinsert, (chatid, 5))
                    conn.commit()
                    bot.sendMessage(update.message.chat_id, text=u"Вы подписались на новости в категории Спорт.")
            except Error as e:
                print(e)
            finally:
                cursor.close()
                conn.close()
    else:
        try:
            cursor = conn.cursor(buffered=True)
            qselect = "SELECT TelegramUserid FROM TelegramSubscribe WHERE NewsCategory=5 AND TelegramUserid = '%s'"
            cursor.execute(qselect, (chatid,))
            if cursor.rowcount != 0:
                qdelete = "DELETE FROM TelegramSubscribe WHERE TelegramUserid='%s' AND NewsCategory=5"
                cursor.execute(qdelete, (chatid,))
                conn.commit()
                bot.sendMessage(update.message.chat_id, text=u"Вы уже подписаны на категорию Спорт. Удаляю подписку.")
            else:
                qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                cursor.execute(qinsert, (chatid, 5))
                conn.commit()
                bot.sendMessage(update.message.chat_id, text=u"Вы подписались на новости в категории Спорт.")
        except Error as e:
            print(e)
        finally:
            cursor.close()
            conn.close()

# подписка и отписка на все категории новостей
def nall(bot, update):
    i=0
    chatid = update.message.chat_id
    userid = update.message.from_user.id
    chat_type = bot.get_chat(chatid)
    conn = mysql.connector.connect(host='', database='', user='', password='')
    if chat_type.type != "private":
        admin = bot.get_chat_administrators(chatid)
        for user_id in admin:
            if user_id.user.id != userid:
                i = i
            else:
                i = i + 1
        if i == 0:
            bot.sendMessage(update.message.chat_id, text=u"Вы не являетесь администратором группы и не можете настраивать бота!")
        else:
            try:
                cursor = conn.cursor(buffered=True)
                qselect = "SELECT TelegramUserId, NewsCategoryTxt FROM TelegramSubscribe INNER JOIN NewsCategory WHERE TelegramSubscribe.NewsCategory=NewsCategory.NewsCategoryId AND TelegramSubscribe.TelegramUserId='%s' ORDER BY NewsCategoryTxt ASC"
                cursor.execute(qselect, (chatid,))
                if cursor.rowcount != 0:
                    txt = u'Вы уже подписаны на категорию: '
                    row = cursor.fetchone()
                    while row is not None:
                        txt = txt + row[1] + u'\n'
                        row = cursor.fetchone()
                    txt = txt + u'Чтобы удалить или добавить категорию, используйте отдельные команды.'
                    bot.sendMessage(update.message.chat_id, text=txt)
                else:
                    for x in range(1, 6):
                        qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                        cursor.execute(qinsert, (chatid, x))
                        conn.commit()
                    bot.sendMessage(update.message.chat_id, text=u"Вы подписались на все категории новостей.")
            except Error as e:
                print(e)
            finally:
                cursor.close()
                conn.close()
    else:
        try:
            cursor = conn.cursor(buffered=True)
            qselect = "SELECT TelegramUserId, NewsCategoryTxt FROM TelegramSubscribe INNER JOIN NewsCategory WHERE TelegramSubscribe.NewsCategory=NewsCategory.NewsCategoryId AND TelegramSubscribe.TelegramUserId='%s' ORDER BY NewsCategoryTxt ASC"
            cursor.execute(qselect, (chatid,))
            if cursor.rowcount != 0:
                txt = u'Вы уже подписаны на категорию: '
                row = cursor.fetchone()
                while row is not None:
                    txt = txt + row[1] + '\n'
                    row = cursor.fetchone()
                txt = txt + u'Чтобы удалить или добавить категорию, используйте отдельные команды.'
                bot.sendMessage(update.message.chat_id, text=txt)
            else:
                for x in range(1, 6):
                    qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                    cursor.execute(qinsert, (chatid, x))
                    conn.commit()
                bot.sendMessage(update.message.chat_id, text=u"Вы подписались на все категории новостей.")
        except Error as e:
            print(e)
        finally:
            cursor.close()
            conn.close()

def send_text_message_to_channel(bot):
    """ Connect to MySQL database """
    try:
        conn = mysql.connector.connect(host='',
                                       database='',
                                       user='',
                                       password='')
        cursor = conn.cursor()
        qselect = "SELECT idNews,txtCaption, txtText FROM News WHERE (logRSSPublish=1 AND logTelegramed=0 AND logActive=1) ORDER BY dtActivation LIMIT 1"
        qupdate = ("UPDATE News SET logTelegramed=1 WHERE idNews = %s ")
        cursor.execute(qselect)

        row = cursor.fetchone()

        if row is not None:
            url = 'http://www.' + unicode(row[0])
            smessage = '*' + unicode(row[1]) + '*\n' + unicode(textshorter(row[2])) + '\n' + url
            bot.sendMessage(chat_id='', text=smessage, parse_mode=telegram.ParseMode.MARKDOWN)
            newsid = int(row[0])
            cursor.execute("""
                UPDATE News SET logTelegramed=1 WHERE idNews = %s
            """ % (newsid))
            conn.commit
        cursor.close()
        conn.close()
    except Error as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


def send_photo_message_to_channel(bot):
    """ Connect to MySQL database """
    try:
        conn = mysql.connector.connect(host='',
                                       database='',
                                       user='',
                                       password='')
        cursor = conn.cursor()
        q_select_news = "SELECT idNews,txtCaption, txtText FROM News WHERE (logRSSPublish=1 AND logTelegramed=0 AND logActive=1) ORDER BY dtActivation LIMIT 1"
        q_select_photo = ("SELECT txtUname FROM NewsPhoto WHERE idnews = %s ORDER BY id LIMIT 1")
        qupdate = ("UPDATE News SET logTelegramed=1 WHERE idNews = %s ")
        cursor.execute(q_select_news)
        row = cursor.fetchone()
        if row is not None:
            news_id = row[0]
            news_caption = unicode(textshorter(row[1]).encode('UTF-8', 'ignore'))
            print(row[1])
            print(news_caption)
            url = 'http://www.' + str(news_id)
            cursor.execute("""
                SELECT txtUname FROM NewsPhoto WHERE idnews = %s ORDER by id LIMIT 1
            """ % (int(news_id)))
            row2 = cursor.fetchone()
            photo_uname = str(row2[0])
            photo_file = '/home/' + str(news_id) + '/' + str(photo_uname)
            s_message = str(news_caption) + '\n' + url
            bot.sendPhoto(chat_id='', photo=open(photo_file, 'rb'), caption=s_message)
            cursor.execute("""
                UPDATE News SET logTelegramed=1 WHERE idNews = %s
            """ % (int(news_id)))
            conn.commit
        cursor.close()
        conn.close()
    except Error as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


def send_photo_message_to_user(bot):
    try:
        conn = mysql.connector.connect(host='',
                                       database='',
                                       user='',
                                       password='')
        conn2 = mysql.connector.connect(host='',
                                        database='',
                                        user='',
                                        password='')
        conn3 = mysql.connector.connect(host='',
                                        database='',
                                        user='',
                                        password='')
        cursor = conn.cursor()
        cursor2 = conn2.cursor()
        cursor3 = conn3.cursor()
        q_select_news = "SELECT `idNews`,`txtCaption`, `txtText`, `idNewsCategory`, `logActive` FROM `News` WHERE (logRSSPublish=1 AND logTelegramed=0 AND logActive=1) ORDER BY dtActivation LIMIT 1"
        q_select_photo = "SELECT txtUname FROM NewsPhoto WHERE idnews = '%s' ORDER by id LIMIT 1"
        q_update = "UPDATE News SET logTelegramed=1 WHERE idNews = '%s'"
        cursor.execute(q_select_news)
        row = cursor.fetchone()
        news_id = row[0]
        news_category = row[3]
        #print(row[1].encode('UTF-8'))
        news_caption = textshorter(row[1].encode('UTF-8'))
        url = 'http://www.' + str(news_id)
        cursor2.execute(q_select_photo,(news_id,))
        row2 = cursor2.fetchone()
        photo_uname = str(row2[0])
        photo_file = '/home/' + str(news_id) + '/' + str(photo_uname)
        s_message = news_caption + u'\n' + url
        #print (s_message.encode('UTF-8'))
        #print (len(s_message))
        q_select_user = "SELECT TelegramUserid FROM TelegramSubscribe WHERE NewsCategory='%s'"
        cursor3.execute(q_select_user, (news_category,))
        row3 = cursor3.fetchone()
        while row3 is not None:
            bot.sendPhoto(chat_id=row3[0], photo=open(photo_file, 'rb'), caption=s_message.encode('UTF-8'), disable_notification=True)
            time.sleep(0.03)
            row3 = cursor3.fetchone()
        cursor.execute(q_update, (news_id,))
        conn.commit
    except Error as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
        cursor2.close()
        conn2.close()
        cursor3.close()
        conn3.close()

def main():
    # Create the EventHandler and pass it your bot's token.
    # komcity.bot
    updater = Updater("")

    jobs = updater.job_queue
    jobs.put(send_photo_message_to_user, 600)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler(u'помощь', help))
    dp.add_handler(CommandHandler("weather", weather))
    dp.add_handler(CommandHandler("pogoda", weather))
    dp.add_handler(CommandHandler(u'погода', weather))
    dp.add_handler(CommandHandler("city", ncity))
    dp.add_handler(CommandHandler("region", nregion))
    dp.add_handler(CommandHandler("accident", naccident))
    dp.add_handler(CommandHandler("culture", nculture))
    dp.add_handler(CommandHandler("sport", nsport))
    dp.add_handler(CommandHandler("all", nall))
    #dp.add_handler(CommandHandler(u'Город', news))
    dp.add_handler(MessageHandler([Filters.text], news))

    # on noncommand i.e message - echo the message on Telegram
    #    dp.add_handler(CommandHandler(echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
