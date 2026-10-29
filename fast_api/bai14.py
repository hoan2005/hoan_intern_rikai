from functools import lru_cache
from fastapi import Depends, FastAPI
from pydantic_settings import BaseSettings


# Định nghĩa lớp cấu hình (Settings)
class Settings(BaseSettings):
  app_name: str = "Default App"
  debug: bool = False

  class Config:
    env_file = ".env"  



@lru_cache()
def get_settings():
  return Settings()


app = FastAPI()



@app.get("/config")
def get_config(settings: Settings = Depends(get_settings)):
  return {"app_name": settings.app_name, "debug": settings.debug}