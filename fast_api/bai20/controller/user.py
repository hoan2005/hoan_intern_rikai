from fastapi import HTTPException, status
from Schemas.user import UserCreate, UserUpdate


fake_users_db: dict[int, dict] = {}
id_counter = 1


def get_all_users() -> list[dict]:
  return list(fake_users_db.values())


def get_user_by_id(user_id: int) -> dict:
  if user_id not in fake_users_db:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Không tìm thấy người dùng với ID: {user_id}",
    )
  return fake_users_db[user_id]


def create_user(user_data: UserCreate) -> dict:
  global id_counter
  
  for u in fake_users_db.values():
    if u["email"] == user_data.email:
      raise HTTPException(
          status_code=status.HTTP_400_BAD_REQUEST,
          detail="Email này đã được đăng ký bởi người dùng khác.",
      )

  user_id = id_counter
  new_user = {
      "id": user_id,
      "username": user_data.username,
      "email": user_data.email,
      "password": user_data.password,  
  }
  fake_users_db[user_id] = new_user
  id_counter += 1
  return new_user


def update_user(user_id: int, user_data: UserUpdate) -> dict:
  existing_user = get_user_by_id(user_id)

  update_data = user_data.model_dump(exclude_unset=True)

  if "email" in update_data:
    for uid, u in fake_users_db.items():
      if uid != user_id and u["email"] == update_data["email"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email này đã được sử dụng."
        )

  existing_user.update(update_data)
  fake_users_db[user_id] = existing_user
  return existing_user


def delete_user(user_id: int) -> dict:
  get_user_by_id(user_id)  # Kiểm tra tồn tại
  deleted_user = fake_users_db.pop(user_id)
  return {"message": f"Đã xóa thành công người dùng có ID: {user_id}"}