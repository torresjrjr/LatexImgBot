#!/usr/bin/python
"""
This is a Telegram Bot which returns rendered images of LaTeX with an API.
"""

import telegram
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters
import requests
import urllib
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)


# constants

try:
    with open('token') as File:
        TOKEN = File.read().splitlines()[0]
except FileNotFoundError as Err:
    print(
"""
You need a bot token to run this Telegram bot. Please make a
file named 'token' with your bot token in there, in the same
folder as your bot file.

Learn more at t.me/botfather
""" )
    quit()

API = "https://latex.codecogs.com/png.latex?" 
EXAMPLE_LATEX = r"x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}"


# callback handlers

def cb_start(upd, ctx):
    first_name = upd.message.from_user.first_name
    upd.message.reply_text(
        f"Hello, {first_name}\n"
        "Type some _LaTeX_ and this bot will "
        "return a rendered image of it.\n\n"

        "Use   /link (_with some LaTeX_)   to also return an image link.\n\n"

        "This bot will support inline queries in the future.\n\n"

        "Try the following:\n"
        "```\n"
        f"{EXAMPLE_LATEX}\n"
        "```\n\n"

        "Author: t.me/torresjrjr",

        parse_mode=telegram.ParseMode.MARKDOWN,
    )


def cb_help(upd, ctx):
    cb_start(upd, ctx)


def cb_echo(upd, ctx):
    ctx.bot.send_message(
        chat_id = upd.effective_chat.id,
        text    = upd.message.text,
    )


def handler(upd, ctx, kind="standard"):
    msg = upd.message.text
    print("Incomming message:", msg)

    if kind == "linked": latex = msg[5:]  # remove the "/link" part
    else:                latex = msg

    encoded_latex = urllib.parse.quote(latex)
    latex_url = API + encoded_latex

    if kind == "standard": caption = f"`{msg}`"
    elif kind == "linked": caption = f"`{msg}`" + "\n" + latex_url

    ctx.bot.send_photo(
        chat_id = upd.effective_chat.id,
        photo   = latex_url,
        caption = caption,
        parse_mode = telegram.ParseMode.MARKDOWN,
    )


cb_link    = lambda upd, ctx: handler(upd, ctx, kind="linked")
cb_handler = lambda upd, ctx: handler(upd, ctx)


# main

def main():
    print("Running...")
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start'     , cb_start))
    dp.add_handler(CommandHandler('help'      , cb_help))
    dp.add_handler(CommandHandler('link'      , cb_link))
    dp.add_handler(MessageHandler(Filters.text, cb_handler))

    updater.start_polling()
    updater.idle()
    print("Done.")


if __name__=='__main__':
    main()
