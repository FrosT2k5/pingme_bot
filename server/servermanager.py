from fastapi import FastAPI,Response,status
from pydantic import BaseModel
from bot.sqlhandler import getusingusername
from telegram.error import Forbidden
import uvicorn

app = FastAPI()

# Define the sendmessage api json
class message_model(BaseModel):
    username: str
    message: str
    securitykey: int

# TODO: This function should later serve static send message form
@app.get("/")
async def root():
    return {"message": "Hello World"}


# Post method to send message, accepts json with username, message and securitykey
@app.post("/api/sendmessage")
async def sendmessage(messagedata: message_model,response: Response):
    from bot import botapplication # TODO: remove this import and make a function in botapplication to handle this
    messagedict = messagedata.dict()
    uid = getusingusername(messagedict['username'])

    if uid == 0:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"status":"error","error": "User not found in database, did you /start the bot?"}
    realsecuritykey = uid[2]

    if realsecuritykey != messagedict['securitykey']:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"status":"error","error": "Invalid Security key"}
    
    if len(messagedict['message']) > 4096:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"status":"error","error":"Message is longer than allowed limit of 4096 characters"}
    
    #Since all above checks passed, security key is right, proceed to message 
    try:
        messagecmd = await botapplication.bot.sendMessage(uid[1],messagedict['message'])
        response.status_code = status.HTTP_200_OK
        return {"status": "success"}
    except Forbidden:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"status":"error","error":"Unable to send message to bot, did you block the bot?"}
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        error = "Unknown error: {e}, please contact the maintainer of bot at Telegram @SuperCosmicBeing"
        return {"status":"error","error": error}
    

# function to start the fastapi server
async def startserver():
    config = uvicorn.Config("server:app", port=5000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()
