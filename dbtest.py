from mysql import connector
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters
import re
import asyncio
import time
import uvicorn

botapplication = ApplicationBuilder().token('2037162393:AAFJFrw4rUKBYLErd10t0qOBYe14AeZqHNA').build()
db = connector.connect(host="s4f.h.filess.io",port="3307",user="testproject_madesaved",password="8626661685b803bad8b71fea42758964f2692df5",database="testproject_madesaved")

dbcursor = db.cursor()

def inserttodb(tguserid, tgusername, securitykey):
    query = "SELECT * from user ORDER BY id DESC LIMIT 1"
    dbcursor.execute(query)
    answer = dbcursor.fetchall()
    if not answer:
        id = 1
    else:
        id = answer[0][0]+1

    query = "INSERT INTO user (id, tguserid, tgusername, securitykey) VALUES (%s,%s,%s,%s)"
    values = (id,tguserid,tgusername,securitykey)
    dbcursor.execute(query,values)
    db.commit()
    print(dbcursor.rowcount, "record inserted.")

def updatepin(tguserid,securitykey,tgusername):
    query = "UPDATE user SET securitykey = %s,tgusername = %s WHERE tguserid = %s"
    values = (securitykey,tgusername,tguserid)
    dbcursor.execute(query,values)
    answer = dbcursor.fetchall()
    return 1

def printfulltable():
    query = "SELECT * FROM user"
    dbcursor.execute(query)
    answer = dbcursor.fetchall()
    for x in answer:
        print(x)

def getusinguserid(userid):
    query = "SELECT * FROM user WHERE tguserid = %s"
    dbcursor.execute(query,[userid])
    answer = dbcursor.fetchall()
    print(answer)
    if not answer:
        return 0
    else:
        return answer[0]

def getusingusername(username):
    query = "SELECT * FROM user WHERE tgusername = %s"
    dbcursor.execute(query,[username])
    answer = dbcursor.fetchall()
    print(answer)
    if not answer:
        return 0
    else:
        return answer[0]


PIN= 1
RESETPIN=1

async def starthandler(update: Update,context: ContextTypes.DEFAULT_TYPE):
    usrid = update.message.from_user.id

    if (getusinguserid(usrid) != 0):
        await update.message.reply_text("You have already setup the bot. Send /resetPin to reset the pin.")
        return ConversationHandler.END
    
    await update.message.reply_text("Hey! Send a 4 digit security pin to continue")
    return PIN

async def pinhandler(update: Update,context: ContextTypes.DEFAULT_TYPE):
    usrmessage = update.message.text

    if re.match("^[0-9]{4}$",usrmessage):
        print("pin: ",usrmessage)
        inserttodb(update.message.from_user.id,update.message.from_user.username,usrmessage)
        await update.message.reply_text("Thank you, pin saved to database. Now you can use the bot")
        printfulltable()
        return ConversationHandler.END
    else:
        await update.message.reply_text("Please send a 4 number which will be your pin")
        return PIN

async def resethandler(update, context):
    await update.message.reply_text("Please send new 4 digit pin.")
    return RESETPIN

async def resetpinhandler(update,context):
    usrmessage = update.message.text
    if re.match("^[0-9]{4}$",usrmessage):
        print("pin: ",usrmessage)
        updatepin(update.message.from_user.id,usrmessage,update.message.from_user.username)
        await update.message.reply_text("Pin Reset Successfully.")
        printfulltable()
        return ConversationHandler.END
    else:
        await update.message.reply_text("Please send a 4 number which will be your pin")
        return RESETPIN

async def getpinhandler(update,context):
    usrid = update.message.from_user.id
    pin = getusinguserid(usrid)
    try:
        pin = pin[2]
    except:
        await update.message.reply_text("Pin: 0")
        return 0
    await update.message.reply_text(f"Pin: {pin}")
   
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

"""
botapplication.add_handler(startconvhandler)
botapplication.add_handler(resetconvhandler)
botapplication.add_handler(CommandHandler("getPin",getpinhandler))
print("Starting Bot")
botapplication.run_polling(allowed_updates=Update.ALL_TYPES)
"""

async def botrunner():
    from server import startserver
    botapplication.add_handler(startconvhandler)
    botapplication.add_handler(resetconvhandler)
    botapplication.add_handler(CommandHandler("getPin",getpinhandler))
    print("Starting Bot")

    async with botapplication as b:
        await b.initialize()
        await b.start()
        await b.updater.start_polling()
        print("Starting server")
        await startserver()
        print("Reached EOL")
        await b.updater.stop()
        await b.stop()
        await b.shutdown()

if __name__ == "__main__":
    asyncio.run(botrunner())