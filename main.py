#!/usr/bin/env python
# -*- coding: utf-8 -*-
import telegram
from telegram.ext import *
from functools import partial
import json
from random import choice
from utils.utils import texter, get_time, args_time
import sys, os

with open("conf/settings.json") as settings:
        SETTINGS = json.load(settings)

# Import the duos and squads manager
# corresponding to the configured database engine
if SETTINGS["USE_DATABASE"]:
    if SETTINGS["DATABASE_ENGINE"] == "postgres":
        pass
    elif SETTINGS["DATABASE_ENGINE"] == "sqlite3":
        pass
else:
    from utils.squaddic import SquadDic
    SquadManager = SquadDic()

# Miscellaneous functions-----------------------------------------------
def send_create_group(bot,cid,message,user,query=False,group=False):
    s_list = "\n"
    if not group:
        group = SquadManager.get_group(user)
    users = SquadManager.get_group_users(group)
    data = " %s %s" % (group,user)
    sym1 = texter("symbol01",SETTINGS["LENGUAGE"])
    sym2 = texter("symbol02",SETTINGS["LENGUAGE"])
    sym3 = texter("symbol03",SETTINGS["LENGUAGE"])
    sym4 = texter("symbol04",SETTINGS["LENGUAGE"])
    count = 0
    for user in users:
        if user[0] is not None:
            count += 1
            if user[2]:
                s = sym2+" "+user[0]+"\n"
            else:
                s = sym3+" "+user[0]+"\n"
        else:
            s = sym1+"\n"
        s_list += s
    message += "\n"+sym4 % (count,len(users))
    message += s_list
    a = [
    [telegram.InlineKeyboardButton(text=texter("btn_group_01",
        SETTINGS["LENGUAGE"]),callback_data="JG"+data)],
    [telegram.InlineKeyboardButton(text=texter("btn_group_02",
        SETTINGS["LENGUAGE"]),callback_data="LG"+data)],
    [telegram.InlineKeyboardButton(text=texter("btn_group_03",
        SETTINGS["LENGUAGE"]),callback_data="UG"+data)]]
    keyboard = telegram.InlineKeyboardMarkup(a)
    if query: 
        bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text=message,
            parse_mode=telegram.ParseMode.HTML,
            reply_markup=keyboard)
    else:
        bot.sendMessage(chat_id=cid,text=message,
            parse_mode=telegram.ParseMode.HTML,
            reply_markup=keyboard)
    
def expire_group(*args):
    SquadManager.expire_group()
    return True
    
def expire_message(bot,job):
    mid,cid = SquadManager.expire_message()
    bot.delete_message(chat_id=cid,message_id=mid)
    return True
    
# General commands -----------------------------------------------------
def command_help(bot, update, pass_chat_data=True):
    cid = update.message.chat_id
    bot.sendMessage(chat_id=cid,
        text=texter("help",SETTINGS["LENGUAGE"]),
        parse_mode=telegram.ParseMode.HTML)
    
def command_about(bot, update, pass_chat_data=True):
    cid = update.message.chat_id
    bot.sendMessage(chat_id=cid, 
        text=texter("about",SETTINGS["LENGUAGE"]),
        parse_mode=telegram.ParseMode.HTML)
    
def command_create_duo(bot,update,args=[],chat_data=True,job_queue=True):
    try:
        cid = update.message.chat_id
        uid = update.message.from_user.id
        user = "@"+str(update.message.from_user.username)
        a = args_time(args)
        if a:
            info = SquadManager.create_duo(user,cid)
            if info == "try_again":
                message = texter("duo02",SETTINGS["LENGUAGE"]) % (user)
                bot.sendMessage(chat_id=cid,text=message,
                    parse_mode=telegram.ParseMode.HTML)
            else:
                a = (a[0],a[1],user)
                message = texter("duo01",SETTINGS["LENGUAGE"]) % a
                send_create_group(bot,cid,message,user)
                job_queue.run_once(expire_group,172800,context=cid)
        else:
            message = texter("duo03",SETTINGS["LENGUAGE"])
            sent = bot.sendMessage(chat_id=cid,text=message,
                parse_mode=telegram.ParseMode.HTML)
            SquadManager.add_message_id(sent.message_id, cid)
            job_queue.run_once(expire_message,45,context=cid)
    except Exception as e:
        print(e)

def command_create_squad(bot,update,args=[],chat_data=True,job_queue=True):
    try:
        cid = update.message.chat_id
        uid = update.message.from_user.id
        user = "@"+str(update.message.from_user.username)
        a = args_time(args)
        if a:
            info = SquadManager.create_squad(user,cid)
            if info == "try_again":
                message = texter("squad02",SETTINGS["LENGUAGE"]) % (user)
                bot.sendMessage(chat_id=cid,text=message,
                    parse_mode=telegram.ParseMode.HTML)
            else:
                a = (a[0],a[1],user)
                message = texter("squad01",SETTINGS["LENGUAGE"]) % a
                send_create_group(bot,cid,message,user)
                job_queue.run_once(expire_group,172800,context=cid)
        else:
            message = texter("squad03",SETTINGS["LENGUAGE"])
            sent = bot.sendMessage(chat_id=cid,text=message,
                parse_mode=telegram.ParseMode.HTML)
            SquadManager.add_message_id(sent.message_id, cid)
            job_queue.run_once(expire_message,45,context=cid)
    except Exception as e:
        print(e)
    
def command_refloat(bot, update, chat_data=True):
    cid = update.message.chat_id
    print(update.message.reply_to_message.message_id)
    bot.sendMessage(chat_id=cid,
        text="<b>refloat:</b> sigue en desarrollo",
        parse_mode=telegram.ParseMode.HTML)

def command_humor(bot, update, pass_chat_data=True):
    cid = update.message.chat_id
    a = ("001","002","003","004","005",
         "006","007","008","009","010",
         "011","012","013")
    pic = "images/humor/humor_"+choice(a)+".jpg"
    bot.sendPhoto(chat_id=cid,
        photo=open(pic,"rb"))

# General --------------------------------------------------------------
def callback_handler(bot, update):
    try:
        query = update.callback_query
        uid = update.callback_query.from_user.id
        cid = query.message.chat_id
        user = "@"+str(query.from_user.username)
        data = query.data.split(" ")
        a = query.message.text.split("\n")[0].split(" ")
        message = "\n".join(query.message.text.split("\n")[0:2])
        expired = False
        
        if data[0] == "JG": # Joint group
            info = SquadManager.join(user,uid,data[1],True)
        elif data[0] == "LG": # Leave group
            info = SquadManager.leave(user,data[1])
        elif data[0] == "UG": # Undecided group
            info = SquadManager.join(user,uid,data[1],False)
        if not info:
            bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text=texter("warning01",SETTINGS["LENGUAGE"]),
                parse_mode=telegram.ParseMode.HTML)
        else:
            send_create_group(bot,cid,message,data[2],query,data[1])
            
    except Exception as e:
        return True
    
def listener(bot, update):
    cid = update.message.chat_id
    message = update.message.text
    print("ID: %s \n Message: %s" % (cid, message))

def main():
    bot = telegram.Bot(token=SETTINGS["TEST_BOT_TOKEN"])
    #bot = telegram.Bot(token=SETTINGS["BOT_TOKEN"])
    botupdater = Updater(bot.token)
    
    # Add handlers
    dp = botupdater.dispatcher
    #dp.add_handler(MessageHandler(Filters.text, listener))
    dp.add_handler(CallbackQueryHandler(callback_handler))

    # Commands handlers 
    dp.add_handler(CommandHandler('help',command_help))
    dp.add_handler(CommandHandler('about',command_about))
    dp.add_handler(CommandHandler('crearDuo',command_create_duo,
        pass_args=True,pass_chat_data=True,pass_job_queue=True))
    dp.add_handler(CommandHandler('crearSquad',command_create_squad,
        pass_args=True,pass_chat_data=True,pass_job_queue=True))
    dp.add_handler(CommandHandler('refloat',command_refloat,
        pass_chat_data=True))
    dp.add_handler(CommandHandler('humor',command_humor))


    # Initialize the bot
    botupdater.start_polling()
    botupdater.idle()

if __name__ == "__main__":
    main()
