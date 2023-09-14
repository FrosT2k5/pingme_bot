from fastapi import FastAPI
import uvicorn

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

async def startserver():
    config = uvicorn.Config("server:app", port=5000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()