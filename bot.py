#!/usr/bin/python
"""
This is a Telegram Bot which returns rendered images of LaTeX using an API.
"""

import telegram
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters
from telegram.error import (TelegramError, Unauthorized, BadRequest, 
                            TimedOut, ChatMigrated, NetworkError)
import datetime
import urllib
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)


# CONSTANTS

try:
    with open('token') as TokenFile:
        TOKEN = TokenFile.read().splitlines()[0]
except FileNotFoundError:
    print(
"""
You need a bot token to run an instance of this Telegram bot.
Please make a file named 'token' with your bot token in there,
in the same folder as this bot file.

Learn more at t.me/botfather
""" )
    quit()

IMAGE_DPI = 512
API = f"https://latex.codecogs.com/png.latex?\\{IMAGE_DPI}dpi&space;%s"
EXAMPLE_LATEX = r"x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}"


# UTIL

# Returns a iso-formatted string of datetime at moment of call.
dt_now = lambda: datetime.datetime.now().isoformat(timespec="seconds")


# CALLBACK HANDLERS

def cb_start(upd, ctx):
    first_name = upd.message.from_user.first_name
    out_msg = f"""Hello, {first_name}
Type some _LaTeX_ and this bot will return a rendered image of it.

Use   /link _(with some LaTeX)_   to also return an image link.

This bot aims to support inline queries in the future.

Try the following:

```
{EXAMPLE_LATEX}
```

Author: t.me/torresjrjr
"""
    upd.message.reply_text(
        out_msg,
        parse_mode=telegram.ParseMode.MARKDOWN,
    )


def cb_help(upd, ctx):
    cb_start(upd, ctx)


def handler(upd, ctx, kind="standard"):
    msg     = upd.message.text
    name    = upd.message.from_user.name
    log_msg = f"{dt_now()} :: {name}\t:: {msg}"
    print(log_msg)

    if kind == "link": latex = msg.replace("/link","")
    else             : latex = msg

    encoded_latex = urllib.parse.quote(latex)
    latex_url     = API % encoded_latex

    if   kind == "standard": caption = f"`{latex}`"
    elif kind == "linked"  : caption = f"`{latex}`" + "\n" + latex_url

    ctx.bot.send_photo(
        chat_id    = upd.effective_chat.id,
        photo      = latex_url,
        caption    = caption,
        parse_mode = telegram.ParseMode.MARKDOWN,
    )


cb_link    = lambda upd, ctx: handler(upd, ctx, kind="link")
cb_handler = lambda upd, ctx: handler(upd, ctx)
cb_QUITBOT = lambda upd, ctx: quit()


def cb_error(update, context):
    try:
        raise context.error
    except Unauthorized as e:
        print("Error:", e)  # remove update.message.chat_id from conversation list
    except BadRequest as e:
        print("Error:", e)  # handle malformed requests - read more below!
    except TimedOut as e:
        print("Error:", e)  # handle slow connection problems
    except NetworkError as e:
        print("Error:", e)  # handle other connection problems
    except ChatMigrated as e:
        print("Error:", e)  # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError as e:
        print("Error:", e)  # handle all other telegram related errors


# MAIN

def main():
    print("Starting bot...")

    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher
    dp.add_error_handler(cb_error)
    dp.add_handler(CommandHandler('start'     , cb_start))
    dp.add_handler(CommandHandler('help'      , cb_help))
    dp.add_handler(CommandHandler('link'      , cb_link))
    dp.add_handler(CommandHandler('QUITBOT'   , cb_QUITBOT))
    dp.add_handler(MessageHandler(Filters.text, cb_handler))

    print(dt_now(), "Serving...")

    updater.start_polling()
    updater.idle()

    print(dt_now(), "Ended.")


if __name__=='__main__':
    main()
