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
import os
import signal
import random

logging.basicConfig(
    filename="log", filemode='a',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt="%H:%M:%S",
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

IMAGE_TYPE = "png"
IMAGE_DPI  = 512
API = f"https://latex.codecogs.com/{IMAGE_TYPE}.latex?\\{IMAGE_DPI}dpi&space;%s"
EXAMPLE_LATEX = r"\text{The quadratic formula} \\ " + "\n" + \
                r"x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}"


# UTIL

# Returns a iso-formatted string of datetime at moment of call.
dt_now = lambda: datetime.datetime.now().isoformat(timespec="seconds")

def logger_dec(old_cb_func):

    def new_cb_func(upd, ctx):
        msg     = upd.message.text
        name    = upd.message.from_user.name
        log_msg = f"{dt_now()} :: {name}\t:: {msg}"
        logging.info(log_msg)
        print(log_msg)

        return old_cb_func(upd, ctx)

    return new_cb_func


def get_random_example():
    example_lines  = []
    recording      = False

    with open("examples.tex", 'r') as File:
        line = next(File)
        if not line.startswith("%TOTAL"):
            raise Exception("No '%TOTAL N' on first line of examples.tex")
        else:
            total_examples = int( line.split()[1] )
            example_number = random.randint(1, total_examples)
            print("Example number", example_number)

        for line in File:
            print(line)
            if line.startswith(f"%BEGIN {example_number}"):
                recording = True
                continue

            if line.startswith("%END") and recording:
                recording = False
                break

            if recording:
                example_lines += [line]

    example = ''.join(example_lines)
    return example


# CALLBACK HANDLERS

@logger_dec
def cb_start(upd, ctx):
    first_name = upd.message.from_user.first_name
    out_msg = f"""\
Hello, {first_name}
Type some _LaTeX_ and this bot will return a rendered image of it.

Use   /link _(with some LaTeX)_   to also return an image link.

This bot aims to support inline queries in the future.

Try the following:

```
{EXAMPLE_LATEX}
```

Or use /random for examples.

Author: t.me/torresjrjr
"""
    upd.message.reply_text(
        out_msg,
        parse_mode=telegram.ParseMode.MARKDOWN,
    )


def cb_help(upd, ctx):
    cb_start(upd, ctx)


@logger_dec
def cb_random(upd, ctx):
    latex = get_random_example()

    encoded_latex = urllib.parse.quote(latex)
    latex_url     = API % encoded_latex

    caption = f"`{latex}`"

    ctx.bot.send_photo(
        chat_id    = upd.effective_chat.id,
        photo      = latex_url,
        caption    = caption,
        parse_mode = telegram.ParseMode.MARKDOWN,
    )


@logger_dec
def handler(upd, ctx, kind="standard"):
    msg = upd.message.text

    if kind == "link": latex = msg.replace("/link","")
    else             : latex = msg

    encoded_latex = urllib.parse.quote(latex)
    latex_url     = API % encoded_latex

    if   kind == "standard": caption = f"`{latex}`"
    elif kind == "link"    : caption = f"`{latex}`\n" + latex_url

    ctx.bot.send_photo(
        chat_id    = upd.effective_chat.id,
        photo      = latex_url,
        caption    = caption,
        parse_mode = telegram.ParseMode.MARKDOWN,
    )


cb_link    = lambda upd, ctx: handler(upd, ctx, kind="link")
cb_handler = lambda upd, ctx: handler(upd, ctx)

@logger_dec
def cb_admin(upd, ctx):
    msg     = upd.message.text
    name    = upd.message.from_user.name
    log_msg = f"{dt_now()} :: {name}\t:: {msg}"
    print(log_msg)

    username = upd.message.from_user.username
    if username == "torresjrjr":
        upd.message.reply_text(
            "Admin authorised. Sending SIGINT...",
            parse_mode=telegram.ParseMode.MARKDOWN,
        )
        os.kill(os.getpid(), signal.SIGINT)


def cb_error(update, context):
    try:
        raise context.error
    except Unauthorized as e:
        print("Unauthorized Error:", e)  # remove update.message.chat_id from conversation list
    except BadRequest as e:
        print("BadRequest Error:", e)  # handle malformed requests - read more below!
    except TimedOut as e:
        print("TimedOut Error:", e)  # handle slow connection problems
    except NetworkError as e:
        print("NetworkError Error:", e)  # handle other connection problems
    except ChatMigrated as e:
        print("ChatMigrated Error:", e)  # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError as e:
        print("TelegramError Error:", e)  # handle all other telegram related errors


# MAIN

def main():
    print("Starting bot...")

    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher
    dp.add_error_handler(cb_error)
    dp.add_handler(CommandHandler('start'     , cb_start))
    dp.add_handler(CommandHandler('help'      , cb_help))
    dp.add_handler(CommandHandler('link'      , cb_link))
    dp.add_handler(CommandHandler('random'    , cb_random))
    dp.add_handler(CommandHandler('admin'     , cb_admin))
    dp.add_handler(MessageHandler(Filters.text, cb_handler))

    print(dt_now(), "Serving...")

    updater.start_polling()
    updater.idle()

    print(dt_now(), "Ended.")


if __name__=='__main__':
    main()
