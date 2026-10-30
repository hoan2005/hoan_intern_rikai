import asyncio
from fastapi import BackgroundTasks, FastAPI
app = FastAPI()
async def send_email_task(email: str, message: str):
  # Giả lập quá trình gọi SMTP server gửi email mất thời gian
  await asyncio.sleep(3)
  print(
      f"[Background Task] Đã gửi thành công email tới {email} với nội dung"
      f" '{message}'"
  )
@app.post("/send-email")
async def send_email(email: str, background_tasks: BackgroundTasks):
  background_tasks.add_task(
      send_email_task, email=email, message="Chào mừng bạn đến với hệ thống!"
  )

  return {"message": "Email queued"}