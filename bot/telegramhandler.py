from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters
from bot.sqlhandler import *
import re
from os import environ

# Constants used in conversation handlers
PIN=1
RESETPIN=1

# bot application object, used in sqlhandler so declared globally
botapplication = ApplicationBuilder().token(environ.get("BOT_TOKEN")).build()


# /start conversation handler, ideally returns to pinhandler conversation function
async def starthandler(update: Update,context: ContextTypes.DEFAULT_TYPE):
    usrid = update.message.from_user.id

    if (getusinguserid(usrid) != 0):
        await update.message.reply_text("You have already setup the bot. Send /resetPin to reset the pin.")
        return ConversationHandler.END
    
    await update.message.reply_text("Hey! Send a 4 digit security pin to continue")
    return PIN

# pinhandler keeps returning itself until correct input is given, then ends Conversation handler
async def pinhandler(update: Update,context: ContextTypes.DEFAULT_TYPE):
    usrmessage = update.message.text

    if re.match("^[0-9]{4}$",usrmessage):
        print("pin: ",usrmessage)
        inserttodb(update.message.from_user.id,update.message.from_user.username,usrmessage)
        await update.message.reply_text("Thank you, pin saved to database. Now you can use the bot")
        return ConversationHandler.END
    else:
        await update.message.reply_text("Please send a 4 number which will be your pin")
        return PIN

# resetpin handler, ideally returns to resetpin conversation function
async def resethandler(update, context):
    await update.message.reply_text("Please send new 4 digit pin.")
    return RESETPIN

# resetpinhandler keeps returning itself until correct input is given, then ends Conversation handler
async def resetpinhandler(update,context):
    usrmessage = update.message.text
    if re.match("^[0-9]{4}$",usrmessage):
        updatepin(update.message.from_user.id,usrmessage,update.message.from_user.username)
        await update.message.reply_text("Pin Reset Successfully. It will take some time for it to reflect in database.")
        return ConversationHandler.END
    else:
        await update.message.reply_text("Please send a 4 number which will be your pin")
        return RESETPIN


# command handler to get pin and send it to user
async def getpinhandler(update,context):
    usrid = update.message.from_user.id
    pin = getusinguserid(usrid)
    try:
        pin = pin[2]
    except:
        await update.message.reply_text("Pin: 0")
        return 0
    await update.message.reply_text(f"Pin: {pin}")
   
def registerhandlers(botapplication):
    # First define the conversation handlers
    startconvhandler = ConversationHandler(
        entry_points=[CommandHandler("start",starthandler)],
        states={
            PIN: [MessageHandler(filters.TEXT, pinhandler)]
        },
        fallbacks=[]
    )

    resetconvhandler = ConversationHandler(
        entry_points=[CommandHandler("resetPin",resethandler)],
        states={
            PIN: [MessageHandler(filters.TEXT, resetpinhandler)]
        },
        fallbacks=[]
    )

    # Add handlers
    botapplication.add_handler(startconvhandler)
    botapplication.add_handler(resetconvhandler)
    botapplication.add_handler(CommandHandler("getPin",getpinhandler))
