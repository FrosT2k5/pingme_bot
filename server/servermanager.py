from fastapi import FastAPI,Response,status,UploadFile,File,Form
from typing import Annotated
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bot.sqlhandler import getusingusername
from telegram.error import Forbidden,TimedOut
import uvicorn
from os import environ
import bot

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the sendmessage api json
class message_model(BaseModel):
    username: str
    message: str
    securitykey: int
    
# Post method to send message, accepts json with username, message and securitykey
@app.post("/api/sendmessage")
async def sendmessage(messagedata: message_model,response: Response):
    botapplication = bot.botapplication # TODO: remove this import and make a function in botapplication to handle this
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
        error = f"Unknown error: {e}, please contact the maintainer of bot at Telegram @SuperCosmicBeing"
        return {"status":"error","error": error}
    
@app.get("/health")
async def healthcheck():
    return {"status":"ok"}

# class properties_model(BaseModel):
#     username: str
#     securitykey: int

@app.post("/api/sendfile")
async def send_file(file: Annotated[UploadFile, File()], username: Annotated[str, Form()], securitykey: Annotated[int, Form()],response: Response):
    uid = getusingusername(username)

    file_content = await file.read()
    file_size = file.file.tell()
    file_size_limit = 50 # tdlib has limit of 50MB for botapi

    if (file_size/1024/1024) > file_size_limit:
        response.status_code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        return {"status": "error","error": f"Filesize is larger than {file_size_limit}MB"}

    if uid == 0:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"status":"error","error": "User not found in database, did you /start the bot?"}
    realsecuritykey = uid[2]

    if realsecuritykey != securitykey:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"status":"error","error": "Invalid Security key"}
    
    botapplication = bot.botapplication
    try:
        await botapplication.bot.send_document(uid[1], file_content, filename=file.filename, write_timeout=35)
        return { "status": "success" }
    except TimedOut:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return { "status": "error", "error": "Telegram timed out, try retrying."}
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        error = f"Unknown error: {e}, please contact the maintainer of bot at Telegram @SuperCosmicBeing"
        return {"status":"error","error": error} 
           
# mount the / to statichtml/ folder so the base url opens up the form
app.mount("/", StaticFiles(directory="server/statichtml/",html=True),name="form")

# function to start the fastapi server
async def startserver():
    config = uvicorn.Config("server:app", host='127.0.0.1', port=int(environ.get("PORT")), log_level="info")
    server = uvicorn.Server(config)
    await server.serve()
