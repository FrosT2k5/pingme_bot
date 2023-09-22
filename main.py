from bot import botapplication,registerhandlers
import asyncio
from sys import argv
from os import environ

useWebhook = False

try:
    webhookarg = argv[1]
    if webhookarg == "webhook":
        useWebhook = True
except IndexError:
    useWebhook = False

def startbotwebhook():
    print("Starting telegram bot using webhook")
    registerhandlers(botapplication)
    botapplication.run_webhook(
        listen = "0.0.0.0",
        port = int(environ.get("PORT")),
        secret_token = environ.get("WEBHOOK_SECRET_TOKEN"),
        webhook_url = environ.get("WEBHOOK_URL")
    )

async def startapiserver():
    from server import startserver
    await startserver()

if __name__ == "__main__":
    if useWebhook:
        startbotwebhook()
    else:
        asyncio.run(startapiserver())