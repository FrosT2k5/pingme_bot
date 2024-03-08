from bot import botapplication,registerhandlers
import asyncio

async def startbot():
    # import startserver function here to avoid error due to cyclical import
    from server import startserver
    print("Starting Bot")
    await registerhandlers(botapplication)

    #start the bot
    async with botapplication as b:
        await b.initialize()
        await b.start()
        await b.updater.start_polling()
        print("Starting server")
        await startserver() # This function starts the fastapi server asynchronously
        print("Reached EOL")
        await b.updater.stop()
        await b.stop()
        await b.shutdown()

if __name__=="__main__":
    asyncio.run(startbot())