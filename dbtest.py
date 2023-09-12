from mysql import connector
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters
import re

botapplication = ApplicationBuilder().token('2037162393:AAFJFrw4rUKBYLErd10t0qOBYe14AeZqHNA').build()
db = connector.connect(host="localhost",user="yash",password="test@123",database="test")

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

def printfulltable():
    query = "SELECT * FROM user"
    dbcursor.execute(query)
    answer = dbcursor.fetchall()
    for x in answer:
        print(x)

def getusinguserid(userid):
    query = f"SELECT * FROM user WHERE tguserid='{userid}'"
    dbcursor.execute(query)
    answer = dbcursor.fetchall()
    print(answer)
    if not answer:
        return 0
    else:
        return answer[0]

PIN= 1

async def starthandler(update,context):
    usrid = update.message.from_user.id

    if (getusinguserid(usrid) != 0):
        await update.message.reply_text("You have already setup the bot. Send /resetPin to reset the pin.")
        return ConversationHandler.END
    
    await update.message.reply_text("Hey! Send a 4 digit security pin to continue")
    return PIN

async def pinhandler(update,context):
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

async def elsehandler(update,context):
    update.message.reply_text("Please enter a 4 digit pin")
    return PIN

convhandler = ConversationHandler(
    entry_points=[CommandHandler("start",starthandler)],
    states={
        PIN: [MessageHandler(filters.TEXT, pinhandler)],
    },
    fallbacks=[]
)

botapplication.add_handler(convhandler)
print("Starting Bot")
botapplication.run_polling(allowed_updates=Update.ALL_TYPES)


#printfulltable()
#print("FETCH: ",getusinguserid(-323))

#inserttodb(-2323,"def",2343)

