import json
from emoji import emojize
import time
import datetime
import pytz

with open("texts/esdialogues.json") as dialogues:
        ES_TEXTS  = json.load(dialogues)


def texter(key,lenguage):
    if lenguage == "es":
        texts = ES_TEXTS
    else:
        texts = ES_TEXTS
    if texts.get(key) is not None:
        if isinstance(texts[key], str):
            return emojize(texts[key])
        elif isinstance(texts[key], list):
            text = ""
            for s in texts[key]:
                text += "\n"+s
            return emojize(text)
        else:
            return "Text not found"
            
def get_time():
    es_tz = pytz.timezone("Europe/Madrid")
    mx_tz = pytz.timezone("America/Chicago")
    es_now = datetime.datetime.now(es_tz)
    mx_now = datetime.datetime.now(mx_tz) 
    h_es = es_now.strftime("%H:%M")
    h_mx = mx_now.strftime("%H:%M")
    return h_es,h_mx
    
def args_time(args):
    try:
        f_args = len(args)
        if args[0] == "es" or args[0] == "mx":
            if f_args >= 2:
                h = int(args[1])
            else:
                return False
            if f_args >= 3:
                m = int(args[2])
            else:
                m = 0
        if args[0] == "es":
            es_h = h
            mx_h = h+17
            return _format_str_time(es_h,m),_format_str_time(mx_h,m)
        elif args[0] == "mx":
            es_h = h+7
            mx_h = h
            return _format_str_time(es_h,m),_format_str_time(mx_h,m)
        else:
            if f_args >= 1:
                h = int(args[0])
            else:
                return False
            if f_args >= 2:
                m = int(args[1])
            else:
                m = 0
            es_h = h
            mx_h = h+17
            return _format_str_time(es_h,m),_format_str_time(mx_h,m)
    except Exception as e:
        return False
        
def _format_str_time(hours,minutes):
    if hours > 23:
        hours = hours%24
    if minutes > 59:
        minutes = minutes%60
    sh,sm= str(hours),str(minutes)
    if len(sh) < 2:
        sh = "0"+sh
    if len(sm) < 2:
        sm = "0"+sm
    return sh+":"+sm
        
    
    
