from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Ok"}


@app.get("/gettests")
async def root():
    return {"message": "Hello world!"}
