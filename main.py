####--------------------------------####
#--# Author:   by uriid1            #--#
#--# License:  GNU GPL              #--#
#--# Telegram: @rp_party            #--#
#--# Mail:     appdurov@gmail.com   #--#
####--------------------------------####
    
####################
## Import libs
import sys
import asyncio
import time
import io
import os
import shutil
import zipfile
import base64
import logging
import random
import glob
import re
from telegraph import upload_file
from telethon import Button
from telethon import events
from telethon.tl.types import ChannelParticipantsAdmins
from telethon import client
from telethon.tl.functions.messages import EditChatDefaultBannedRightsRequest
from telethon.tl.functions.messages import ImportChatInviteRequest as Get
from datetime import datetime
from asyncio import sleep
from asyncio.exceptions import TimeoutError
from telethon import functions, types
from telethon import events
from telethon.tl.functions.channels import EditBannedRequest, GetFullChannelRequest, GetParticipantsRequest, EditAdminRequest, EditPhotoRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.messages import GetFullChatRequest, GetHistoryRequest, ExportChatInviteRequest
from telethon.errors import ChannelInvalidError, ChannelPrivateError, ChannelPublicGroupNaError, BadRequestError, ChatAdminRequiredError, FloodWaitError, MessageNotModifiedError, UserAdminInvalidError
from telethon.errors.rpcerrorlist import YouBlockedUserError, UserAdminInvalidError, UserIdInvalidError
from telethon.tl.functions.channels import GetFullChannelRequest as getchat
from telethon.tl.functions.phone import CreateGroupCallRequest as startvc
from telethon.tl.functions.phone import DiscardGroupCallRequest as stopvc
from telethon.tl.functions.phone import GetGroupCallRequest as getvc
from telethon.tl.functions.phone import InviteToGroupCallRequest as invitetovc
from telethon.errors import ImageProcessFailedError, PhotoCropSizeSmallError
from telethon.tl.types import ChatAdminRights, InputChatPhotoEmpty, MessageMediaPhoto
from telethon.tl.types import ChannelParticipantsKicked, ChannelParticipantAdmin, ChatBannedRights, ChannelParticipantCreator, ChannelParticipantsAdmins, ChannelParticipantsBots, MessageActionChannelMigrateFrom, UserStatusEmpty, UserStatusLastMonth, UserStatusLastWeek, UserStatusOffline, UserStatusOnline, UserStatusRecently
from telethon.utils import get_display_name, get_input_location, get_extension
from os import remove
from math import sqrt
from prettytable import PrettyTable
from emoji import emojize
from pathlib import Path
from userbot import iqthon
from userbot.utils import admin_cmd, sudo_cmd, eor
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from . import humanbytes
from . import BOTLOG, BOTLOG_CHATID, admin_groups, get_user_from_event, extract_time
from ..utils.tools import create_supergroup
from ..helpers import reply_id, readable_time
from ..helpers.utils import _format, get_user_from_event, reply_id
from ..helpers import media_type
from ..helpers.google_image_download import googleimagesdownload
from ..helpers.tools import media_type
from ..sql_helper.locks_sql import get_locks, is_locked, update_lock
from ..utils import is_admin
from . import progress
from ..sql_helper import gban_sql_helper as gban_sql
from ..sql_helper.mute_sql import is_muted, mute, unmute
from ..sql_helper.autopost_sql import add_post, get_all_post, is_post, remove_post
from ..sql_helper import no_log_pms_sql
from ..sql_helper.globals import addgvar, gvarstatus
BANNED_RIGHTS = ChatBannedRights(until_date=None, view_messages=True, send_messages=True, send_media=True, send_stickers=True, send_gifs=True, send_games=True, send_inline=True, embed_links=True)
KLANR_RIGHTS = ChatBannedRights(until_date=None, view_messages=True, send_messages=True, send_media=True, send_stickers=True, send_gifs=True, send_games=True, send_inline=True, embed_links=True)
UNBAN_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=None,
    send_media=None,
    send_stickers=None,
    send_gifs=None,
    send_games=None,
    send_inline=None,
    embed_links=None,
)
LOGS = logging.getLogger(__name__)
plugin_category = "utils"
MUTE = gvarstatus("OR_MUTE") or "(ميوت|كتم)"

###########################
## Console color print
red    = [206, 76,  54]
green  = [68,  250, 123]
blue   = [253, 127, 233]
yellow = [241, 250, 118]
orange = [255, 184, 107]
def colored(color, text):
    return "\033[38;2;{};{};{}m{}\033[38;2;255;255;255m".format(color[0], color[1], color[2], text)


###########################
## Settings
api_id   = int(sys.argv[1])
api_hash = str(sys.argv[2])

## Connect
client = TelegramClient('users/current_user', api_id, api_hash)
client.start()


####################
## Account info
####################
entity = client.get_entity("me")
MY_ID = entity.id
print(
        "["
        + colored(green, "PROFILE: ")
        + str(entity.first_name)
        + " | " + colored(orange, "Id: ") + str(MY_ID)
        + " | " + colored(orange, "Uname: ") + "@" + str(entity.username)
        + "]"
)


########################
## Check script work
## CMD: ping
########################
@client.on(events.NewMessage(outgoing=True, pattern='ping'))
async def handler(event):
    if event.message.from_id.user_id != MY_ID:
        return

    m = await event.respond('pong')
    await asyncio.sleep(1)
    await client.delete_messages(event.chat_id, [event.id, m.id])



#################
## Typing
## CMD: .t
## ARG: text
#################
@iqthon.on(admin_cmd(pattern=f"{MUTE}(?:\s|$)([\s\S]*)"))
async def startmute(event):
    if event.is_private:
        replied_user = await event.client.get_entity(event.chat_id)
        if is_muted(event.chat_id, event.chat_id):
            return await event.edit(                "هذاالشخص بلفعل مكتوم "            )
        if event.chat_id == iqthon.uid:
            return await edit_delete(event, "لايمكنك كتم نفسك")
        try:
            mute(event.chat_id, event.chat_id)
        except Exception as e:
            await event.edit(f"**خطأ :**\n`{e}`")
        else:
            await event.edit("تم كتم الشخص")
        if BOTLOG:
            await event.client.send_message(                BOTLOG_CHATID,                "كتم وقتي \n"                f"**الشخص :** [{replied_user.first_name}](tg://user?id={event.chat_id})\n",            )
    else:
        chat = await event.get_chat()
        admin = chat.admin_rights
        creator = chat.creator
        if not admin and not creator:
            return await edit_or_reply(                event, "عذراليس لديك صلاحيه ادمن"            )
        user, reason = await get_user_from_event(event)
        if not user:
            return
        if user.id == iqthon.uid:
            return await edit_or_reply(event, "عذرا لايمكنك كتم نفسك")
        if user.id == 1226408155:
            return await edit_or_reply(event, "**- دي لا يمڪنني كتـم مبرمج السـورس **")
        if user.id == 428577454:
            return await edit_or_reply(event, "**- دي لا يمڪنني كتـم مبرمج السـورس **")
        userid = user.id
        if is_muted(user.id, event.chat_id):
            return await edit_or_reply(                event, "هذاالشخص بلفعل مكتوم"            )
        result = await event.client.get_permissions(event.chat_id, user.id)
        try:
            if result.participant.banned_rights.send_messages:
                return await edit_or_reply(                    event,                    "هذا الشخص بلفعل مكتوم",                )
        except AttributeError:
            pass
        except Exception as e:
            return await edit_or_reply(event, f"**خطأ : **`{e}`")
        try:
            await event.client(EditBannedRequest(event.chat_id, user.id, MUTE_RIGHTS))
        except UserAdminInvalidError:
            if "admin_rights" in vars(chat) and vars(chat)["admin_rights"] is not None:
                if chat.admin_rights.delete_messages is not True:
                    return await edit_or_reply(                        event,                        "عذرا لايمكنك كتمه لاتوجد لديك صلاحيات ادمن",                    )
            elif "creator" not in vars(chat):
                return await edit_or_reply(                    event, "عذرا لايمكنك كتمه لاتوجد لديك صلاحيات ادمن"                )
            mute(user.id, event.chat_id)
        except Exception as e:
            return await edit_or_reply(event, f"**خطأ : **`{e}`")
        if reason:
            await edit_or_reply(                event,                f"{_format.mentionuser(user.first_name ,user.id)} هذا الشخص مكتوم {get_display_name(await event.get_chat())}`\n"                f"السبب : {reason}",            )
        else:
            await edit_or_reply(                event,                f"{_format.mentionuser(user.first_name ,user.id)} هذا الشخص مكتوم {get_display_name(await event.get_chat())}`\n",            )
        if BOTLOG:
            await event.client.send_message(                BOTLOG_CHATID,                "كتم \n"                f"**الشخص :** [{user.first_name}](tg://user?id={user.id})\n"                f"**المحادثه :** {get_display_name(await event.get_chat())}(`{event.chat_id}`)",            )



######################
## Heart Animation
## CMD: .heart
## ARG: text
######################
heart_emoji = [
    "✨-💎",
    "✨-🌺",
    "☁️-😘",
    "✨-🌸",
    "🌾-🐸",
    "🔫-💥",
    "☁️-💟",
    "🍀-💖",
    "🌴-🐼",
]

edit_heart = '''
1 2 2 1 2 2 1
2 2 2 2 2 2 2
2 2 2 2 2 2 2
1 2 2 2 2 2 1
1 1 2 2 2 1 1
 1 1 1 2 1 1
'''

@client.on(events.NewMessage(pattern=".heart+"))
async def handler(event):
    if event.message.from_id.user_id != MY_ID:
        return

    try:
        text = event.message.message.replace(".heart ", "")
        if text == ".heart":
            text = "Хочешь так же? Подпишись @S0XSU"

        message   = event.message
        chat      = event.chat_id

        # play anim
        frame_index = 0
        while(frame_index != len(heart_emoji)):
            await client.edit_message(chat, message, edit_heart.replace("1", heart_emoji[frame_index].split("-")[0])
                                                               .replace("2", heart_emoji[frame_index].split("-")[1]))
            await asyncio.sleep(1)
            frame_index = frame_index + 1

        await client.edit_message(chat, message, text)
    except:
        print( "[" + colored(red, "Error") + "] " + "Не удалось выполнить команду [.heart] Возможно вы словили flood." )



## RUN
client.run_until_disconnected()
