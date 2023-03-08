#import telegram
import logging
from typing import List
from telegram import Update, InputMediaPhoto, constants, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes, ApplicationHandlerStop, TypeHandler, CallbackQueryHandler, CommandHandler
from telegram.ext.filters import MessageFilter
from functools import wraps
#import misc
import os

#Variables
PATH = os.path.abspath(os.path.dirname(__file__))
BOT_TOKEN = None
BOT_TOKEN_FILE = "bot_token.cfg"
ALLOWED_USERS = []
ALLOWED_USERS_FILE = "allowed_users.cfg"

#Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(os.path.join(PATH, "errorlog.log")),
        logging.StreamHandler()
    ],
    level=logging.INFO
)

#LOAD Setting
#LOAD TOKEN
try:
    with open(os.path.join(PATH, BOT_TOKEN_FILE), 'r') as file:
        lines = file.readlines()
        TOKEN = lines[0].strip()
        logging.info(f"LOADED TOKEN {TOKEN} from {BOT_TOKEN_FILE}")

except:
    with open(os.path.join(PATH, ALLOWED_USERS_FILE), 'w') as file:
        file.write("#DELETE THIS LINE AND ADD YOUR ALLOW USERS CHAT_ID!")
    logging.error(f"CHECK YOUR {ALLOWED_USERS_FILE}")
    pass

#LOAD ALLOWED_USERS
try:
    with open(os.path.join(PATH, ALLOWED_USERS_FILE), 'r') as file:
        lines = file.readlines()
        for line in Lines:
            ALLOWED_USERS.append(int(line.strip()))
            logging.info(f"LOADED USER {line} from {ALLOWED_USERS_FILE}")

except:
    with open(os.path.join(PATH, ALLOWED_USERS_FILE), 'w') as file:
        file.write("#DELETE THIS LINE AND ADD YOUR ALLOW USERS CHAT_ID!")
    logging.error(f"CHECK YOUR {ALLOWED_USERS_FILE}")
    pass


#Handle MESSAGES and COMMANDS
#check if the user is allowed to use the bot by comparing the user id to the ALLOWED_USERS array
async def checkRights(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in ALLOWED_USERS:
        #Do nothing and continue with the other handlers
        pass
    else:
        #Reply to the user and send his chat_id for the admin to add to the allowed user list if necessary
        await update.effective_message.reply_text(f"Hey {update.effective_user.full_name}! \n\nYou are not allowed to use me (yet)!\nPlease contact the ADMINISTRATOR of the bot with the following ID and ask him to unlock you. \n\nID: {update.effective_chat.id}")
        raise ApplicationHandlerStop
    
#Handle TEXT MESSAGES NOT containing a command
async def textmessage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.effective_message.id, text=update.effective_message.text)

#Handle TEXT REPLIES
async def textreply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.effective_message.id, text="You replied to my message 🥺")

#Handle EVERYTHING NOT A MESSAGE OR COMMAND
async def unused(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.effective_message.id, text="Sorry. Can't help you with that 😣")

#Handle the /START command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Hi {update.effective_user.full_name}! \nI am a BOT.🤖  \nTo get startet type /help!")

#Handle the /HELP command
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Here's where I would put a helpful message.\n\n\nIF I HAD ONE!")

#Handle UNKNOWN commands
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command 🤖\nTo get startet type /help")

#DEBUG

#Main
if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    #Check USER rights
    application.add_handler(TypeHandler(Update, checkRights), -1)

    #Handle TEXT Messages
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND) & (~filters.REPLY), textmessage))

    #Handle TEXT REPLIES
    application.add_handler(MessageHandler(filters.REPLY & filters.TEXT, textreply))

    #Handle UNUSED or NOT YET IMPLEMENTED
    application.add_handler(MessageHandler((~filters.TEXT) & (~filters.COMMAND), unused))

    #Handle COMMANDS
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(MessageHandler(filters.COMMAND, unknown))

    #Run POLLING to get UPDATES
    application.run_polling()