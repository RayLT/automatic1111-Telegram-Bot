#imports telegram
import logging
from telegram import Update, InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes, ApplicationHandlerStop, TypeHandler, CallbackQueryHandler, CommandHandler

#imports automatic1111
import webuiapi
from PIL import Image
import io

#imports misc
import os
import json
import requests

#Variables
PATH = os.path.abspath(os.path.dirname(__file__))
NSFW_TAGS = []

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

#Tools
def settings_to_json():
    with open(os.path.join(PATH, SETTINGS_FILE), 'w') as settings_file:
        json.dump(settings,settings_file, indent=4)

def image_to_byte_array(image: Image) -> bytes:
  # BytesIO is a file-like buffer stored in memory
  imgByteArr = io.BytesIO()
  # image.save expects a file-like as a argument
  image.save(imgByteArr, format=image.format)
  # Turn the BytesIO object back into a bytes object
  imgByteArr = imgByteArr.getvalue()
  return imgByteArr

def load_nsfw_tags():
    try:
        NSFW_TAGS.clear()
        response = requests.get("https://raw.githubusercontent.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words/master/en")
        text = response.text

        # save each line to a list
        lines = io.StringIO(text).readlines()

        # print the list of lines
        for line in lines:
            striped_line = line.strip()
            NSFW_TAGS.append(striped_line)
        return True
    except:
        return False

def numberToEmoji(number):
    number_string = str(number)
    emojis = {
    '0': '0️⃣',
    '1': '1️⃣',
    '2': '2️⃣',
    '3': '3️⃣',
    '4': '4️⃣',
    '5': '5️⃣',
    '6': '6️⃣',
    '7': '7️⃣',
    '8': '8️⃣',
    '9': '9️⃣'
    }
    result = ""
    for digit in number_string:
        if digit in emojis:
            result += emojis[digit]
    return result

def hasNSFW(input):
    if len(NSFW_TAGS) == 0:
        if not load_nsfw_tags():
            logging.error("Could not load NSFW Tags")
            return False
        else:
            for line in NSFW_TAGS:
                if line in input:
                    return True 
    else:
        for line in NSFW_TAGS:
            print(line)
            if line in input:
                print("found NSFW")
                return True
    print("no NSFW found")
    return False

#Settings
SETTINGS_FILE = "settings.cfg"
settings = {
    "general_settings" : {
        "bot_token" : "",
        "allowed_users" : [],
        "check_nsfw" : False,
        "max_steps" : 100,
        "max_batch" : 30
    },
    "diffusion_settings" : {
        "prompt" : "a duck with sunglasses",
        "negative_prompt" : "",
        "width" : 512,
        "height" : 512,
        "batch_size" : 1,
        "styles" : [""],
        "model" : "v1-5-pruned-emaonly",
        "sampler" : "",
        "steps" : 30,
        "restore_faces" : True,
        "cfg" : 7.0
    }
}

#Load Settings
try:
    with open(os.path.join(PATH, SETTINGS_FILE), 'r') as settings_file:
        settings = json.load(settings_file)
        BOT_TOKEN = settings["general_settings"]["bot_token"]
        ALLOWED_USERS = settings["general_settings"]["allowed_users"]
except:
    settings_to_json()
    logging.error(f"CHECK YOUR {SETTINGS_FILE}")
    exit()

#Create Client for automatic1111
api = webuiapi.WebUIApi()

async def generateImage():
    cur_mod = api.util_get_current_model()
    if not settings["diffusion_settings"]["model"] == "" and not settings["diffusion_settings"]["model"] in cur_mod:
        api.util_set_model(settings["diffusion_settings"]["model"])

    result = api.txt2img(
            prompt=settings["diffusion_settings"]["prompt"],
            negative_prompt=settings["diffusion_settings"]["negative_prompt"],
            restore_faces=settings["diffusion_settings"]["restore_faces"],
            styles=settings["diffusion_settings"]["styles"],
            cfg_scale=settings["diffusion_settings"]["cfg"],
            width=settings["diffusion_settings"]["width"],
            height=settings["diffusion_settings"]["height"],
            batch_size=settings["diffusion_settings"]["batch_size"],
            sampler_index=settings["diffusion_settings"]["sampler"],
            steps=settings["diffusion_settings"]["steps"]
            )
    images = []
    for im in result.images:
        images.append(image_to_byte_array(im))

    return images, result.parameters

async def sendImage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.effective_message.reply_text(f'generating {numberToEmoji(settings["diffusion_settings"]["batch_size"])} image(s)...\n please hang tight')

    images, info = await generateImage()

    if settings["general_settings"]["check_nsfw"] == True:
        nsfw = hasNSFW(settings["diffusion_settings"]["prompt"])
        print("has nsfw")
    else:
        nsfw = False
        print("no nsfw")

    if len(images) == 1:
        #await context.bot.send_photo(chat_id=update.effective_chat.id, photo=images[0], caption=json.dumps(info, indent=4))
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=images[0], has_spoiler=nsfw, caption=settings["diffusion_settings"]["prompt"])
    else:
        batch_size = settings["diffusion_settings"]["batch_size"]
        quotient = batch_size // 10
        remainder = batch_size % 10
        for i in range(quotient):
            media_group = []
            count = 0
            for p in range(10):
                media_group.append(InputMediaPhoto(images[p+(10*i)], has_spoiler=nsfw,  caption = settings["diffusion_settings"]["prompt"] if count == 0 else ''))
                count += 1
            await context.bot.send_media_group(chat_id=update.effective_chat.id, media=media_group)
        
        if remainder > 0:
            media_group = []
            count = 0
            for i in range(remainder):
                media_group.append(InputMediaPhoto(images[i+(10*quotient)], has_spoiler=nsfw,  caption = settings["diffusion_settings"]["prompt"] if count == 0 else ''))
                count += 1
            await context.bot.send_media_group(chat_id=update.effective_chat.id, media=media_group)
          

    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=msg.id)



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
    prompt = update.effective_message.text

    negative_prompt = ""

    try:
        negative_prompt = prompt.split('[')[1].split(']')[0]
        prompt = prompt.replace(f"[{negative_prompt}]", "")
    except IndexError:
        pass

    settings["diffusion_settings"]["prompt"] = prompt
    settings["diffusion_settings"]["negative_prompt"] = negative_prompt
    settings_to_json()
    await sendImage(update, context)

#Handle the /LAST command
async def last(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await sendImage(update, context)

#Handle TEXT REPLIES
#Only works with media groups if replied to first image in group, others dont have captions in order to show the caption of the media group
async def textreply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_bot = update.message.reply_to_message.from_user
    media_caption = update.message.reply_to_message.caption
    media_group_caption = update.message.reply_to_message
    print(media_group_caption)
    if is_bot and not media_caption == None:
        settings["diffusion_settings"]["prompt"] =  media_caption + " " + update.effective_message.text
        settings_to_json()
        await sendImage(update, context)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.effective_message.id, text="No valid caption found 🥺")

#Handle EVERYTHING NOT A MESSAGE OR COMMAND
async def unused(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, reply_to_message_id=update.effective_message.id, text="Sorry. Can't help you with that 😣")

#Handle the /START command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Hi {update.effective_user.full_name}! \nI am a BOT.🤖  \nTo get startet type /help!")

#Handle the /HELP command
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Here's where I would put a helpful message.\n\n\nIF I HAD ONE!")

#Handle the /BATCH command
async def batch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    batch_size = None
    max_batch_size = settings["general_settings"]["max_batch"]
    error_msg = f"argument error \noptional argument for /batch is a single integer between 1 and {max_batch_size}\n\nyou can change the max_batch in your settings.cfg"
    if len(context.args) == 1:
        try:
            if isinstance(int(context.args[0]), int):
                temp_batch_size = int(context.args[0])
                if 0 < temp_batch_size <= max_batch_size:
                    batch_size = temp_batch_size
                    await update.effective_message.reply_text(f"Set batch size to {batch_size}")
                    settings["diffusion_settings"]["batch_size"] = batch_size
                    settings_to_json()
                else:
                    await update.effective_message.reply_text(error_msg)
        except:
            await update.effective_message.reply_text(error_msg)
            return
    elif len(context.args) > 1:
        await update.effective_message.reply_text(error_msg)
    else:
       await update.effective_message.reply_text(f'Current batch size: {settings["diffusion_settings"]["batch_size"]}')

#Handle the /CFG command
async def cfg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cfg = None
    if len(context.args) == 1:
        try:
            temp_cfg = float(context.args[0]) 
            cfg = temp_cfg
            await update.effective_message.reply_text(f"Set cfg scale size to {cfg}")
            settings["diffusion_settings"]["cfg"] = cfg
            settings_to_json()
        except:
            await update.effective_message.reply_text(f"argument error \noptional argument for /cfg is a single float >0")
    elif len(context.args) > 3:
        await update.effective_message.reply_text(f"argument error \noptional argument for /cfg is a single float >0")
    else:
       await update.effective_message.reply_text(f'Current cfg scale: {settings["diffusion_settings"]["cfg"]}') 

#Handle the /STEPS command
async def steps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    steps = None
    max_steps = settings["general_settings"]["max_steps"]
    error_msg = f"argument error \noptional argument for /steps is a single float between 1 and {max_steps}\n\nyou can change the max_steps in your settings.cfg"
    if len(context.args) == 1:
        try:
            if isinstance(int(context.args[0]), int):
                temp_steps = int(context.args[0])
                if 0 < temp_steps <= max_steps:
                    steps = temp_steps
                    await update.effective_message.reply_text(f"Set STEPS to {steps}")
                    settings["diffusion_settings"]["steps"] = steps
                    settings_to_json()
                else:
                    await update.effective_message.reply_text(error_msg)
        except:
            await update.effective_message.reply_text(error_msg)
            return
    elif len(context.args) > 1:
            await update.effective_message.reply_text(error_msg)
    else:
       await update.effective_message.reply_text(f'Current STEPS: {settings["diffusion_settings"]["steps"]}')

#Handle the /STEPS command
async def current_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    out = ""

    for key, value in settings["diffusion_settings"].items():
        # print the key and value in the desired format
        out += f"{key.upper()}: {value}\n"
    await update.effective_message.reply_text(f'Current SETTINGS: \n\n{out}')

#Handle the /SIZE command
async def size(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #Max Size defined by telegram --> https://limits.tginfo.me/en
    #Sends a message with three inline buttons attached.
    prefix = "size"
    keyval = ["square", "portrait", "landscape", "⬅️"]

    keyboard = [
        [
            InlineKeyboardButton(keyval[0], callback_data=prefix+keyval[0]),
            InlineKeyboardButton(keyval[1], callback_data=prefix+keyval[1]),
        ],
        [InlineKeyboardButton(keyval[2], callback_data=prefix+keyval[2])],
        [InlineKeyboardButton(keyval[3], callback_data=prefix+keyval[3])]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please choose a SIZE:", reply_markup=reply_markup)

#Handle the /MODEL command
async def model(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    prefix = "model"
    api.refresh_checkpoints()
    models = api.get_sd_models()

    keyboard = []

    for t in models:
        keyboard.append([InlineKeyboardButton(text=t["model_name"], callback_data=prefix+t["model_name"])])

    keyboard.append([InlineKeyboardButton(text="⬅️", callback_data=prefix+"cancel")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(f'Current model: {settings["diffusion_settings"]["model"]}', reply_markup=reply_markup)

#Handle the /STYLE command
async def style(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    prefix = "style"
    styles = api.get_prompt_styles()

    keyboard = []

    for s in styles:
        keyboard.append([InlineKeyboardButton(text=s["name"], callback_data=prefix+s["name"])])

    keyboard.append([InlineKeyboardButton(text="NONE", callback_data=prefix+"none")])
    keyboard.append([InlineKeyboardButton(text="⬅️", callback_data=prefix+"cancel")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(f'Current style: {settings["diffusion_settings"]["styles"]}', reply_markup=reply_markup)

#Handle the /SAMPLER command
async def sampler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    prefix = "sampler"
    samplers = api.get_samplers()

    keyboard = []

    for s in samplers:
        keyboard.append([InlineKeyboardButton(text=s["name"], callback_data=prefix+s["name"])])

    keyboard.append([InlineKeyboardButton(text="⬅️", callback_data=prefix+"cancel")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(f'Current style: {settings["diffusion_settings"]["styles"]}', reply_markup=reply_markup)

#Handle the /FACES command
async def faces(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    prefix = "faces"
    keyboard = [
        [
            InlineKeyboardButton("👍", callback_data=prefix+"YES"),
            InlineKeyboardButton("👎", callback_data=prefix+"NO"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f'Restore faces? Currently {str(settings["diffusion_settings"]["restore_faces"]).upper()}', reply_markup=reply_markup)

#Handle the /NSFW command
async def nsfw(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    prefix = "nsfw"
    keyboard = [
        [
            InlineKeyboardButton("👍", callback_data=prefix+"YES"),
            InlineKeyboardButton("👎", callback_data=prefix+"NO"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f'Check for NSFW? Currently {str(settings["general_settings"]["check_nsfw"]).upper()}', reply_markup=reply_markup)


#Handle UNKNOWN commands
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command 🤖\nTo get startet type /help")

#Handle Buttons
async def button_size(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    data = query.data.replace("size", '')

    if data == "cancel":
        await query.edit_message_text(text="canceled")
        pass
    else:
        match data:
            case "square":
                settings["diffusion_settings"]["width"] = 512
                settings["diffusion_settings"]["height"] = 512
            case "portrait":
                settings["diffusion_settings"]["width"] = 512
                settings["diffusion_settings"]["height"] = 768
            case "landscape":
                settings["diffusion_settings"]["width"] = 768
                settings["diffusion_settings"]["height"] = 512
        await query.edit_message_text(text=f"set aspect ratio to {data}")
        settings_to_json()

async def button_model(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data.replace("model", '')
    if data == "cancel":
        await query.edit_message_text(text="canceled")
        pass
    else:
        api.util_set_model(data)
        settings["diffusion_settings"]["model"] = data
        settings_to_json()
        await query.edit_message_text(text=f"set model to {data}")

async def button_style(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data.replace("style", '')
    if data == "cancel":
        await query.edit_message_text(text="canceled")
        pass
    elif data == "none":
        settings["diffusion_settings"]["styles"] = [""]
        settings_to_json()
        await query.edit_message_text(text=f"set style to NONE")
    else:
        settings["diffusion_settings"]["styles"] = [data]
        settings_to_json()
        await query.edit_message_text(text=f"set style to {data}")

async def button_sampler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data.replace("sampler", '')
    if data == "cancel":
        await query.edit_message_text(text="canceled")
        pass
    else:
        samplers = api.get_samplers()
        for s in samplers:
            if s["name"] == data:
                if len(s["aliases"]) > 0:
                    settings["diffusion_settings"]["sampler"] = str(s["aliases"][0])
                else:
                    settings["diffusion_settings"]["sampler"] = s["name"]
                settings_to_json()
                await query.edit_message_text(text=f"set sampler to {data}")

async def button_faces(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data.replace("faces", '')
    match data:
        case "YES":
            settings["diffusion_settings"]["restore_faces"] = True
            await query.edit_message_text(text="RESTORING faces")
        case "NO":
            settings["diffusion_settings"]["restore_faces"] = False
            await query.edit_message_text(text="NOT RESTORING faces")
    settings_to_json()

async def button_nsfw(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data.replace("nsfw", '')
    match data:
        case "YES":
            settings["general_settings"]["check_nsfw"] = True
            await query.edit_message_text(text="CHECKING for NSFW")
        case "NO":
            settings["general_settings"]["check_nsfw"] = False
            await query.edit_message_text(text="NOT CHECKING for NSFW")
    settings_to_json()


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
    application.add_handler(CommandHandler("batch", batch))
    application.add_handler(CommandHandler("last", last))
    application.add_handler(CommandHandler("cfg", cfg))
    application.add_handler(CommandHandler("steps", steps))
    application.add_handler(CommandHandler("settings", current_settings))


    application.add_handler(CommandHandler("size", size))
    application.add_handler(CallbackQueryHandler(button_size, pattern=r"^size"))
    application.add_handler(CommandHandler("model", model))
    application.add_handler(CallbackQueryHandler(button_model, pattern=r"^model"))
    application.add_handler(CommandHandler("style", style))
    application.add_handler(CallbackQueryHandler(button_style, pattern=r"^style"))
    application.add_handler(CommandHandler("sampler", sampler))
    application.add_handler(CallbackQueryHandler(button_sampler, pattern=r"^sampler"))
    application.add_handler(CommandHandler("faces", faces))
    application.add_handler(CallbackQueryHandler(button_faces, pattern=r"^faces"))
    application.add_handler(CommandHandler("nsfw", nsfw))
    application.add_handler(CallbackQueryHandler(button_nsfw, pattern=r"^nsfw"))
    application.add_handler(MessageHandler(filters.COMMAND, unknown))

    #Run POLLING to get UPDATES
    application.run_polling()