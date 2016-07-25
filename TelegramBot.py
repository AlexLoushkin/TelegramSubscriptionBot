#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram
import requests
import logging
import mysql.connector
from mysql.connector import Error
import re
import urllib
#can be used later in order to meet 30 msgs per sec limit
#import time

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    replymarkup = telegram.ReplyKeyboardMarkup([[telegram.KeyboardButton('City'), telegram.KeyboardButton('Region'),
                                                 telegram.KeyboardButton('Accidents'),
                                                 telegram.KeyboardButton('Culture'),
                                                 telegram.KeyboardButton('Sport'),
                                                 telegram.KeyboardButton('All')]], resize_keyboard=True,
                                               one_time_keyboard=True)
    url = u'komcity.ru website bot greets you!' + u'\n' + u'You can subscribe for news messages of certain categories by pressing regarding buttons' + u'\n' + u'or by commands:' + u'\n' + u'City or /city - city news,' + u'\n' + u'Region or /region - region news,' + u'\n' + u'Accidents or /accidents - accidents news,' + u'\n' + u'Culture or /culture - culture news,' + u'\n' + u'Sport or /sport - sport news,' + u'\n' + u'All or /all - all categories. Also shows all catagories you are subscribed for' + u'\n' + u'/weather - shows current weather.' + u'\n' + u'To unsubscribe from news messages choose a category one more time' + u'\n'
    bot.sendMessage(update.message.chat_id, text=url.encode('UTF-8'), reply_markup=replymarkup)

def help(bot, update):
    replymarkup = telegram.ReplyKeyboardMarkup([[telegram.KeyboardButton('City'), telegram.KeyboardButton('Region'),
                                                 telegram.KeyboardButton('Accidents'),
                                                 telegram.KeyboardButton('Culture'),
                                                 telegram.KeyboardButton('Sport'),
                                                 telegram.KeyboardButton('All')]], resize_keyboard=True,
                                               one_time_keyboard=True)
    url = u'komcity.ru website bot greets you!' + u'\n' + u'You can subscribe for news messages of certain categories by pressing regarding buttons' + u'\n' + u'or by commands:' + u'\n' + u'City or /city - city news,' + u'\n' + u'Region or /region - region news,' + u'\n' + u'Accidents or /accidents - accidents news,' + u'\n' + u'Culture or /culture - culture news,' + u'\n' + u'Sport or /sport - sport news,' + u'\n' + u'All or /all - all categories. Also shows all catagories you are subscribed for' + u'\n' + u'/weather - shows current weather.' + u'\n' + u'To unsubscribe from news messages choose a category one more time' + u'\n'
    bot.sendMessage(update.message.chat_id, text=url.encode('UTF-8'), reply_markup=replymarkup)

# def echo(bot, update):
#    bot.sendMessage(update.message.chat_id, text=update.message.text)

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

#shows current weather from our local weather forecast station
def weather(bot, update):
    weatherurl = 'http://www.'
    weatherresponse = requests.get(weatherurl)
    weatherjson = weatherresponse.json()
    phantomtemp = weatherjson['outdoortemp']
    if weatherjson['outdoortemp'] == weatherjson['heatindex']:
        phantomtemp = weatherjson['windchill']
    else:
        phantomtemp = weatherjson['heatindex']
    msg = u'Текущая погода:' + "\n"
    msg = msg + u"Температура воздуха: " + weatherjson['outdoortemp'] + u" °C" + "\n"
    msg = msg + u"Ощущаемая температура: " + phantomtemp + u" °C" + "\n"
    msg = msg + u"Ветер: " + weatherjson['windrosedirection'] + " " + weatherjson['windspeed'] + u" м/c" + "\n"
    msg = msg + u"Относительная влажность воздуха: " + weatherjson['hum'] + u"%" + "\n"
    msg = msg + u"Атмосферное давление: " + weatherjson['baropressure'] + u" мм.рт.ст. " + weatherjson[
        'barotrend'] + "\n"
    msg = msg + "\n"
    msg = msg + u'Прогноз: ' + "\n" + weatherjson['frule'] + "\n"
    bot.sendMessage(update.message.chat_id, text=msg)

#shortens text from a news
def textshorter(text):
    str = text.splitlines()
    if len(str) > 2:
        result = str[0] + str[1]
    else:
        result = str[0]
    if len(result) > 300:
        result = result[:300] + '...'
    return (result)

#options for keyboard. The bot can be used in groups also.
def news(bot, update):
    replytxt = update.message.text
    chatid = update.message.chat_id
    userid = update.message.from_user.id
    chat_type = bot.get_chat(chatid)
    conn = mysql.connector.connect(host='', database='', user='', password='')
    #if chat is not one-to-one we have to check if a message is from a group's admin or creator
    if chat_type.type != "private":
        admin = bot.get_chat_administrators(chatid)
        for user_id in admin:
            if user_id.user.id != userid:
                bot.sendMessage(update.message.chat_id,
                                text="You are not a group admin so you can not set the subscription!")
            else:
                if replytxt == u'City' or replytxt == u'city':
                    try:
                        cursor = conn.cursor(buffered=True)
                        qselect = "SELECT TelegramUserid FROM TelegramSubscribe WHERE NewsCategory=1 AND TelegramUserid = '%s'"
                        cursor.execute(qselect, (chatid,))
                        #if there is already a subscription for this category it will be deleted
                        if cursor.rowcount != 0:
                            bot.sendMessage(update.message.chat_id,
                                            text="You are alredy subscribed for the City category. The subscription has been removed.")
                            qdelete = "DELETE FROM TelegramSubscribe WHERE TelegramUserid='%s' AND NewsCategory=1"
                            cursor.execute(qdelete, (chatid,))
                            conn.commit()
                        else:
                            qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                            cursor.execute(qinsert, (chatid, 1))
                            conn.commit()
                            bot.sendMessage(update.message.chat_id, text="You are now subscribed for the City news category.")
                    except Error as e:
                        print(e)
                    finally:
                        cursor.close()
                        conn.close()
                elif replytxt == u'Region' or replytxt == u'region':
                    try:
                        cursor = conn.cursor(buffered=True)
                        qselect = "SELECT TelegramUserid FROM TelegramSubscribe WHERE NewsCategory=2 AND TelegramUserid = '%s'"
                        cursor.execute(qselect, (chatid,))
                        if cursor.rowcount != 0:
                            bot.sendMessage(update.message.chat_id,
                                            text="You are alredy subscribed for the Region category. The subscription has been removed.")
                            qdelete = "DELETE FROM TelegramSubscribe WHERE TelegramUserid='%s' AND NewsCategory=2"
                            cursor.execute(qdelete, (chatid,))
                            conn.commit()
                        else:
                            qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                            cursor.execute(qinsert, (chatid, 2))
                            conn.commit()
                            bot.sendMessage(update.message.chat_id, text="You are now subscribed for the Region news category.")
                    except Error as e:
                        print(e)
                    finally:
                        cursor.close()
                        conn.close()
                elif replytxt == u'Accidents' or replytxt == u'accidents':
                    try:
                        cursor = conn.cursor(buffered=True)
                        qselect = "SELECT TelegramUserid FROM TelegramSubscribe WHERE NewsCategory=3 AND TelegramUserid = '%s'"
                        cursor.execute(qselect, (chatid,))
                        if cursor.rowcount != 0:
                            bot.sendMessage(update.message.chat_id,
                                            text="You are alredy subscribed for the Accidents category. The subscription has been removed.")
                            qdelete = "DELETE FROM TelegramSubscribe WHERE TelegramUserid='%s' AND NewsCategory=3"
                            cursor.execute(qdelete, (chatid,))
                            conn.commit()
                        else:
                            qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                            cursor.execute(qinsert, (chatid, 3))
                            conn.commit()
                            bot.sendMessage(update.message.chat_id,
                                            text="You are now subscribed for the Accidents news category.")
                    except Error as e:
                        print(e)
                    finally:
                        cursor.close()
                        conn.close()
                elif replytxt == u'Culture' or replytxt == u'culture':
                    try:
                        cursor = conn.cursor(buffered=True)
                        qselect = "SELECT TelegramUserid FROM TelegramSubscribe WHERE NewsCategory=4 AND TelegramUserid = '%s'"
                        cursor.execute(qselect, (chatid,))
                        if cursor.rowcount != 0:
                            bot.sendMessage(update.message.chat_id,
                                            text="You are alredy subscribed for the Culture category. The subscription has been removed.")
                            qdelete = "DELETE FROM TelegramSubscribe WHERE TelegramUserid='%s' AND NewsCategory=4"
                            cursor.execute(qdelete, (chatid,))
                            conn.commit()
                        else:
                            qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                            cursor.execute(qinsert, (chatid, 4))
                            conn.commit()
                            bot.sendMessage(update.message.chat_id,
                                            text="You are now subscribed for the Culture news category.")
                    except Error as e:
                        print(e)
                    finally:
                        cursor.close()
                        conn.close()
                elif replytxt == u'Sport' or replytxt == u'sport':
                    try:
                        cursor = conn.cursor(buffered=True)
                        qselect = "SELECT TelegramUserid FROM TelegramSubscribe WHERE NewsCategory=5 AND TelegramUserid = '%s'"
                        cursor.execute(qselect, (chatid,))
                        if cursor.rowcount != 0:
                            bot.sendMessage(update.message.chat_id,
                                            text="You are alredy subscribed for the Sport category. The subscription has been removed.")
                            qdelete = "DELETE FROM TelegramSubscribe WHERE TelegramUserid='%s' AND NewsCategory=4"
                            cursor.execute(qdelete, (chatid,))
                            conn.commit()
                        else:
                            qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                            cursor.execute(qinsert, (chatid, 5))
                            conn.commit()
                            bot.sendMessage(update.message.chat_id, text="You are now subscribed for the Sport news category.")
                    except Error as e:
                        print(e)
                    finally:
                        cursor.close()
                        conn.close()
                elif replytxt == u'All' or replytxt == u'all':
                    try:
                        cursor = conn.cursor(buffered=True)
                        qselect = "SELECT TelegramUserId, NewsCategoryTxt FROM TelegramSubscribe INNER JOIN NewsCategory WHERE TelegramSubscribe.NewsCategory=NewsCategory.NewsCategoryId AND TelegramSubscribe.TelegramUserId='%s' ORDER BY NewsCategoryTxt ASC"
                        cursor.execute(qselect, (chatid,))
                        if cursor.rowcount != 0:
                            txt = u'You are already subscribed for:' + '\n'
                            row = cursor.fetchone()
                            while row is not None:
                                txt = txt + row[1] + u'\n'
                                row = cursor.fetchone()
                            txt = txt + u'In order to add or remove a category use commands from help.'
                            bot.sendMessage(update.message.chat_id, text=txt)
                        else:
                            for x in range(1, 6):
                                qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                                cursor.execute(qinsert, (chatid, x))
                                conn.commit()
                            bot.sendMessage(update.message.chat_id, text="You are now subscribed for All news categories.")
                    except Error as e:
                        print(e)
                    finally:
                        cursor.close()
                        conn.close()
                else:
                    bot.sendMessage(update.message.chat_id, text=u'Wrong command. Type /help.')
    else:
    	#if a chat is private
        if replytxt == u'City' or replytxt == u'city':
                    try:
                        cursor = conn.cursor(buffered=True)
                        qselect = "SELECT TelegramUserid FROM TelegramSubscribe WHERE NewsCategory=1 AND TelegramUserid = '%s'"
                        cursor.execute(qselect, (chatid,))
                        #if there is already a subscription for this category it will be deleted
                        if cursor.rowcount != 0:
                            bot.sendMessage(update.message.chat_id,
                                            text="You are alredy subscribed for the City category. The subscription has been removed.")
                            qdelete = "DELETE FROM TelegramSubscribe WHERE TelegramUserid='%s' AND NewsCategory=1"
                            cursor.execute(qdelete, (chatid,))
                            conn.commit()
                        else:
                            qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                            cursor.execute(qinsert, (chatid, 1))
                            conn.commit()
                            bot.sendMessage(update.message.chat_id, text="You are now subscribed for the City news category.")
                    except Error as e:
                        print(e)
                    finally:
                        cursor.close()
                        conn.close()
                elif replytxt == u'Region' or replytxt == u'region':
                    try:
                        cursor = conn.cursor(buffered=True)
                        qselect = "SELECT TelegramUserid FROM TelegramSubscribe WHERE NewsCategory=2 AND TelegramUserid = '%s'"
                        cursor.execute(qselect, (chatid,))
                        if cursor.rowcount != 0:
                            bot.sendMessage(update.message.chat_id,
                                            text="You are alredy subscribed for the Region category. The subscription has been removed.")
                            qdelete = "DELETE FROM TelegramSubscribe WHERE TelegramUserid='%s' AND NewsCategory=2"
                            cursor.execute(qdelete, (chatid,))
                            conn.commit()
                        else:
                            qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                            cursor.execute(qinsert, (chatid, 2))
                            conn.commit()
                            bot.sendMessage(update.message.chat_id, text="You are now subscribed for the Region news category.")
                    except Error as e:
                        print(e)
                    finally:
                        cursor.close()
                        conn.close()
                elif replytxt == u'Accidents' or replytxt == u'accidents':
                    try:
                        cursor = conn.cursor(buffered=True)
                        qselect = "SELECT TelegramUserid FROM TelegramSubscribe WHERE NewsCategory=3 AND TelegramUserid = '%s'"
                        cursor.execute(qselect, (chatid,))
                        if cursor.rowcount != 0:
                            bot.sendMessage(update.message.chat_id,
                                            text="You are alredy subscribed for the Accidents category. The subscription has been removed.")
                            qdelete = "DELETE FROM TelegramSubscribe WHERE TelegramUserid='%s' AND NewsCategory=3"
                            cursor.execute(qdelete, (chatid,))
                            conn.commit()
                        else:
                            qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                            cursor.execute(qinsert, (chatid, 3))
                            conn.commit()
                            bot.sendMessage(update.message.chat_id,
                                            text="You are now subscribed for the Accidents news category.")
                    except Error as e:
                        print(e)
                    finally:
                        cursor.close()
                        conn.close()
                elif replytxt == u'Culture' or replytxt == u'culture':
                    try:
                        cursor = conn.cursor(buffered=True)
                        qselect = "SELECT TelegramUserid FROM TelegramSubscribe WHERE NewsCategory=4 AND TelegramUserid = '%s'"
                        cursor.execute(qselect, (chatid,))
                        if cursor.rowcount != 0:
                            bot.sendMessage(update.message.chat_id,
                                            text="You are alredy subscribed for the Culture category. The subscription has been removed.")
                            qdelete = "DELETE FROM TelegramSubscribe WHERE TelegramUserid='%s' AND NewsCategory=4"
                            cursor.execute(qdelete, (chatid,))
                            conn.commit()
                        else:
                            qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                            cursor.execute(qinsert, (chatid, 4))
                            conn.commit()
                            bot.sendMessage(update.message.chat_id,
                                            text="You are now subscribed for the Culture news category.")
                    except Error as e:
                        print(e)
                    finally:
                        cursor.close()
                        conn.close()
                elif replytxt == u'Sport' or replytxt == u'sport':
                    try:
                        cursor = conn.cursor(buffered=True)
                        qselect = "SELECT TelegramUserid FROM TelegramSubscribe WHERE NewsCategory=5 AND TelegramUserid = '%s'"
                        cursor.execute(qselect, (chatid,))
                        if cursor.rowcount != 0:
                            bot.sendMessage(update.message.chat_id,
                                            text="You are alredy subscribed for the Sport category. The subscription has been removed.")
                            qdelete = "DELETE FROM TelegramSubscribe WHERE TelegramUserid='%s' AND NewsCategory=4"
                            cursor.execute(qdelete, (chatid,))
                            conn.commit()
                        else:
                            qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                            cursor.execute(qinsert, (chatid, 5))
                            conn.commit()
                            bot.sendMessage(update.message.chat_id, text="You are now subscribed for the Sport news category.")
                    except Error as e:
                        print(e)
                    finally:
                        cursor.close()
                        conn.close()
                elif replytxt == u'All' or replytxt == u'all':
                    try:
                        cursor = conn.cursor(buffered=True)
                        qselect = "SELECT TelegramUserId, NewsCategoryTxt FROM TelegramSubscribe INNER JOIN NewsCategory WHERE TelegramSubscribe.NewsCategory=NewsCategory.NewsCategoryId AND TelegramSubscribe.TelegramUserId='%s' ORDER BY NewsCategoryTxt ASC"
                        cursor.execute(qselect, (chatid,))
                        if cursor.rowcount != 0:
                            txt = u'You are already subscribed for:' + '\n'
                            row = cursor.fetchone()
                            while row is not None:
                                txt = txt + row[1] + u'\n'
                                row = cursor.fetchone()
                            txt = txt + u'In order to add or remove a category use commands from help.'
                            bot.sendMessage(update.message.chat_id, text=txt)
                        else:
                            for x in range(1, 6):
                                qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                                cursor.execute(qinsert, (chatid, x))
                                conn.commit()
                            bot.sendMessage(update.message.chat_id, text="You are now subscribed for All news categories.")
                    except Error as e:
                        print(e)
                    finally:
                        cursor.close()
                        conn.close()
                else:
                    bot.sendMessage(update.message.chat_id, text=u'Wrong command. Type /help.')
        else:
            bot.sendMessage(update.message.chat_id, text=u'Wrong command. Type /help.')

#the same City subscription but as a command
def ncity(bot, update):
    chatid = update.message.chat_id
    userid = update.message.from_user.id
    chat_type = bot.get_chat(chatid)
    conn = mysql.connector.connect(host='', database='', user='', password='')
    if chat_type.type != "private":
        admin = bot.get_chat_administrators(chatid)
        for user_id in admin:
            if user_id.user.id != userid:
                bot.sendMessage(update.message.chat_id,
                                text="You are not a group admin so you can not set the subscription!")
            else:
                try:
                    cursor = conn.cursor(buffered=True)
                    qselect = "SELECT TelegramUserid FROM TelegramSubscribe WHERE NewsCategory=1 AND TelegramUserid = '%s'"
                    cursor.execute(qselect, (chatid,))
                    if cursor.rowcount != 0:
                        bot.sendMessage(update.message.chat_id,
                                        text="You are alredy subscribed for the City category. The subscription has been removed.")
                        qdelete = "DELETE FROM TelegramSubscribe WHERE TelegramUserid='%s' AND NewsCategory=1"
                        cursor.execute(qdelete, (chatid,))
                        conn.commit()
                    else:
                        qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                        cursor.execute(qinsert, (chatid, 1))
                        conn.commit()
                        bot.sendMessage(update.message.chat_id, text="You are now subscribed for the City news category.")
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
                bot.sendMessage(update.message.chat_id, text="You are alredy subscribed for the City category. The subscription has been removed.")
            else:
                qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                cursor.execute(qinsert, (chatid, 1))
                conn.commit()
                bot.sendMessage(update.message.chat_id, text="You are now subscribed for the City news category.")
        except Error as e:
            print(e)
        finally:
            cursor.close()
            conn.close()

#Region
def nregion(bot, update):
    chatid = update.message.chat_id
    userid = update.message.from_user.id
    chat_type = bot.get_chat(chatid)
    conn = mysql.connector.connect(host='', database='', user='', password='')
    if chat_type.type != "private":
        admin = bot.get_chat_administrators(chatid)
        for user_id in admin:
            if user_id.user.id != userid:
                bot.sendMessage(update.message.chat_id,
                                text="You are not a group admin so you can not set the subscription!")
            else:
                try:
                    cursor = conn.cursor(buffered=True)
                    qselect = "SELECT TelegramUserid FROM TelegramSubscribe WHERE NewsCategory=2 AND TelegramUserid = '%s'"
                    cursor.execute(qselect, (chatid,))
                    if cursor.rowcount != 0:
                        bot.sendMessage(update.message.chat_id,
                                        text="You are alredy subscribed for the Region category. The subscription has been removed.")
                        qdelete = "DELETE FROM TelegramSubscribe WHERE TelegramUserid='%s' AND NewsCategory=2"
                        cursor.execute(qdelete, (chatid,))
                        conn.commit()
                    else:
                        qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                        cursor.execute(qinsert, (chatid, 2))
                        conn.commit()
                        bot.sendMessage(update.message.chat_id, text="You are now subscribed for the Region news category.")
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
                bot.sendMessage(update.message.chat_id, text="You are alredy subscribed for the Region category. The subscription has been removed.")
            else:
                qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                cursor.execute(qinsert, (chatid, 2))
                conn.commit()
                bot.sendMessage(update.message.chat_id, text="You are now subscribed for the Region news category.")
        except Error as e:
            print(e)
        finally:
            cursor.close()
            conn.close()

# Accidents
def naccidents(bot, update):
    chatid = update.message.chat_id
    userid = update.message.from_user.id
    chat_type = bot.get_chat(chatid)
    conn = mysql.connector.connect(host='', database='', user='', password='')
    if chat_type.type != "private":
        admin = bot.get_chat_administrators(chatid)
        for user_id in admin:
            if user_id.user.id != userid:
                bot.sendMessage(update.message.chat_id,
                                text="You are not a group admin so you can not set the subscription!")
            else:
                try:
                    cursor = conn.cursor(buffered=True)
                    qselect = "SELECT TelegramUserid FROM TelegramSubscribe WHERE NewsCategory=3 AND TelegramUserid = '%s'"
                    cursor.execute(qselect, (chatid,))
                    if cursor.rowcount != 0:
                        bot.sendMessage(update.message.chat_id,
                                        text="You are alredy subscribed for the Accidents category. The subscription has been removed.")
                        qdelete = "DELETE FROM TelegramSubscribe WHERE TelegramUserid='%s' AND NewsCategory=3"
                        cursor.execute(qdelete, (chatid,))
                        conn.commit()
                    else:
                        qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                        cursor.execute(qinsert, (chatid, 3))
                        conn.commit()
                        bot.sendMessage(update.message.chat_id,
                                        text="You are now subscribed for the Accidents news category.")
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
                                text="You are alredy subscribed for the Accidents category. The subscription has been removed.")
            else:
                qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                cursor.execute(qinsert, (chatid, 3))
                conn.commit()
                bot.sendMessage(update.message.chat_id, text="You are now subscribed for the Accidents news category.")
        except Error as e:
            print(e)
        finally:
            cursor.close()
            conn.close()

# Culture
def nculture(bot, update):
    chatid = update.message.chat_id
    userid = update.message.from_user.id
    chat_type = bot.get_chat(chatid)
    conn = mysql.connector.connect(host='', database='', user='', password='')
    if chat_type.type != "private":
        admin = bot.get_chat_administrators(chatid)
        for user_id in admin:
            if user_id.user.id != userid:
                bot.sendMessage(update.message.chat_id,
                                text="You are not a group admin so you can not set the subscription!")
            else:
                try:
                    cursor = conn.cursor(buffered=True)
                    qselect = "SELECT TelegramUserid FROM TelegramSubscribe WHERE NewsCategory=4 AND TelegramUserid = '%s'"
                    cursor.execute(qselect, (chatid,))
                    if cursor.rowcount != 0:
                        bot.sendMessage(update.message.chat_id,
                                        text="You are alredy subscribed for the Culture category. The subscription has been removed.")
                        qdelete = "DELETE FROM TelegramSubscribe WHERE TelegramUserid='%s' AND NewsCategory=4"
                        cursor.execute(qdelete, (chatid,))
                        conn.commit()
                    else:
                        qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                        cursor.execute(qinsert, (chatid, 4))
                        conn.commit()
                        bot.sendMessage(update.message.chat_id, text="You are now subscribed for the Culture news category.")
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
                bot.sendMessage(update.message.chat_id, text="You are alredy subscribed for the Culture category. The subscription has been removed.")
            else:
                qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                cursor.execute(qinsert, (chatid, 4))
                conn.commit()
                bot.sendMessage(update.message.chat_id, text="You are now subscribed for the Culture news category.")
        except Error as e:
            print(e)
        finally:
            cursor.close()
            conn.close()

#Sport
def nsport(bot, update):
    chatid = update.message.chat_id
    userid = update.message.from_user.id
    chat_type = bot.get_chat(chatid)
    conn = mysql.connector.connect(host='', database='', user='', password='')
    if chat_type.type != "private":
        admin = bot.get_chat_administrators(chatid)
        for user_id in admin:
            if user_id.user.id != userid:
                bot.sendMessage(update.message.chat_id,
                                text="You are not a group admin so you can not set the subscription!")
            else:
                try:
                    cursor = conn.cursor(buffered=True)
                    qselect = "SELECT TelegramUserid FROM TelegramSubscribe WHERE NewsCategory=5 AND TelegramUserid = '%s'"
                    cursor.execute(qselect, (chatid,))
                    if cursor.rowcount != 0:
                        bot.sendMessage(update.message.chat_id,
                                        text="You are alredy subscribed for the Sport category. The subscription has been removed.")
                        qdelete = "DELETE FROM TelegramSubscribe WHERE TelegramUserid='%s' AND NewsCategory=5"
                        cursor.execute(qdelete, (chatid,))
                        conn.commit()
                    else:
                        qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                        cursor.execute(qinsert, (chatid, 5))
                        conn.commit()
                        bot.sendMessage(update.message.chat_id, text="You are now subscribed for the Sport news category.")
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
                bot.sendMessage(update.message.chat_id, text="You are alredy subscribed for the Sport category. The subscription has been removed.")
            else:
                qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                cursor.execute(qinsert, (chatid, 5))
                conn.commit()
                bot.sendMessage(update.message.chat_id, text="You are now subscribed for the Sport news category.")
        except Error as e:
            print(e)
        finally:
            cursor.close()
            conn.close()

#All
def nall(bot, update):
    chatid = update.message.chat_id
    userid = update.message.from_user.id
    chat_type = bot.get_chat(chatid)
    conn = mysql.connector.connect(host='', database='', user='', password='')
    if chat_type.type != "private":
        admin = bot.get_chat_administrators(chatid)
        for user_id in admin:
            if user_id.user.id != userid:
                bot.sendMessage(update.message.chat_id,
                                text="You are not a group admin so you can not set the subscription!")
            else:
                try:
                    cursor = conn.cursor(buffered=True)
                    qselect = "SELECT TelegramUserId, NewsCategoryTxt FROM TelegramSubscribe INNER JOIN NewsCategory WHERE TelegramSubscribe.NewsCategory=NewsCategory.NewsCategoryId AND TelegramSubscribe.TelegramUserId='%s' ORDER BY NewsCategoryTxt ASC"
                    cursor.execute(qselect, (chatid,))
                    if cursor.rowcount != 0:
                        txt = u'You are already subscribed for:'+'\n'
                        row = cursor.fetchone()
                        while row is not None:
                            txt = txt + row[1] + u'\n'
                            row = cursor.fetchone()
                        txt = txt + u'In order to add or delete a category use commands'
                        bot.sendMessage(update.message.chat_id, text=txt)
                    else:
                        for x in range(1, 6):
                            qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                            cursor.execute(qinsert, (chatid, x))
                            conn.commit()
                        bot.sendMessage(update.message.chat_id, text="You are now subscribed for the All news categories.")
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
                txt = u'You are already subscribed for:'+'\n'
                row = cursor.fetchone()
                while row is not None:
                    txt = txt + row[1] + u'\n'
                    row = cursor.fetchone()
                txt = txt + u'In order to add or delete a category use commands'
                bot.sendMessage(update.message.chat_id, text=txt)
            else:
                for x in range(1, 6):
                    qinsert = "INSERT INTO TelegramSubscribe (TelegramUserid, NewsCategory) VALUES(%s,%s)"
                    cursor.execute(qinsert, (chatid, x))
                    conn.commit()
                bot.sendMessage(update.message.chat_id, text="You are now subscribed for the All news categories.")
        except Error as e:
            print(e)
        finally:
            cursor.close()
            conn.close()

#send one latest news of a certain category to all subscribers 
def send_photo_message_to_user(bot):
    try:
        #due to limitations of conn we need 3 different connections to the same db in order for our queries not to get messed up. 
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
        q_select_news = "SELECT `idNews`,`txtCaption`, `txtText`, `idNewsCategory`, `logActive` FROM `News` WHERE (logRSSPublish=1 AND TelegramTest=0 AND logActive=1) ORDER BY dtActivation LIMIT 1"
        q_select_photo = "SELECT txtUname FROM NewsPhoto WHERE idnews = '%s' ORDER by id LIMIT 1"
        q_update = "UPDATE News SET TelegramTest=1 WHERE idNews = '%s'"
        cursor.execute(q_select_news)
        row = cursor.fetchone()
        while row is not None:
            news_id = row[0]
            news_category = row[3]
            news_caption = unicode(row[1]).encode('UTF-8', 'ignore')
            url = 'http://www./news/?id=' + str(news_id)
            cursor2.execute(q_select_photo,(news_id,))
            row2 = cursor2.fetchone()
            photo_uname = str(row2[0])
            photo_file = '/home/.../news/' + str(news_id) + '/' + str(photo_uname)
            s_message = news_caption + '\n' + url
            q_select_user = "SELECT TelegramUserid FROM TelegramSubscribe WHERE NewsCategory='%s'"
            cursor3.execute(q_select_user, (news_category,))
            row3 = cursor3.fetchone()
            while row3 is not None:
                bot.sendPhoto(chat_id=row3[0], photo=open(photo_file, 'rb'), caption=s_message)
				#when bot sends >30 msgs per sec Telegram can put restrictions on it             
                # time.sleep(0.5)
                row3 = cursor3.fetchone()
            cursor.execute(q_update,(news_id,))
            conn.commit
            row = cursor.fetchone()
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
    updater = Updater("YourToken")

    #putting our bot on job queue every 30 secs so as soon as a news appears in db it will be sent to subscribers withing that time
    jobs = updater.job_queue
    jobs.put(send_photo_message_to_user, 30)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("weather", weather))
    dp.add_handler(CommandHandler("city", ncity))
    dp.add_handler(CommandHandler("region", nregion))
    dp.add_handler(CommandHandler("accidents", naccidents))
    dp.add_handler(CommandHandler("culture", nculture))
    dp.add_handler(CommandHandler("sport", nsport))
    dp.add_handler(CommandHandler("all", nall))
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
