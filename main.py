from bot import botapplication,registerhandlers
import asyncio
from sys import argv
from os import environ

async def startbot():
    # import startserver function here to avoid error due to cyclical import
    from server import startserver
    print("Starting Bot")
    await registerhandlers(botapplication)

    useWebhook = False

    try:
        webhookarg = argv[1]
        if webhookarg == "webhook":
            useWebhook = True
    except IndexError:
        useWebhook = False

    #start the bot
    async with botapplication as b:
        if useWebhook:
            print("Using webhook")
            await b.initialize()
            await b.start()
            await b.updater.start_webhook(
                listen = "0.0.0.0",
                url_path="1",
                port = int(environ.get("PORT")),
                secret_token = "frost2k5",
                webhook_url = "https://pingme.domcloud.io/1"
            )
            await startserver()
            await b.updater.stop()
            await b.stop()
            await b.shutdown()

        else:
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