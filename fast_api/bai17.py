import os
from fastapi import FastAPI, File, HTTPException, UploadFile, status

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


MAX_FILE_SIZE = 5 * 1024 * 1024  # 5,242,880 bytes


@app.post("/upload")
async def upload_avatar(avatar: UploadFile = File(...)):

  file_ext = os.path.splitext(avatar.filename)[1].lower()
  if file_ext not in ALLOWED_EXTENSIONS:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Unsupported file type",
    )

  contents = await avatar.read()
  if len(contents) > MAX_FILE_SIZE:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Unsupported file type",  
    )


  file_path = os.path.join(UPLOAD_DIR, avatar.filename)
  with open(file_path, "wb") as f:
    f.write(contents)

  return {"filename": avatar.filename}