import asyncio
from fastapi import FastAPI

app = FastAPI()


@app.get("/async-demo")
async def async_demo():

  await asyncio.sleep(2)

  return {"message": "Completed"}