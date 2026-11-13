import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.dependencies import get_current_user
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import Collection, Note, User


@pytest.fixture
def api():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        users = [
            User(
                email="user1@gmail.com",
                password_hash="not-used",
                full_name="User One",
            ),
            User(
                email="user2@gmail.com",
                password_hash="not-used",
                full_name="User Two",
            ),
        ]
        db.add_all(users)
        db.commit()
        user_ids = [user.id for user in users]

    active_user_id = {"value": user_ids[0]}

    def override_get_db():
        with Session(engine) as db:
            yield db

    def override_get_current_user() -> User:
        return User(id=active_user_id["value"])

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    with TestClient(app) as client:
        yield client, engine, user_ids, active_user_id
    app.dependency_overrides.clear()
    engine.dispose()


def test_collection_crud_and_validation(api):
    client, _, _, _ = api
    response = client.post(
        "/collections",
        json={"name": "  Cá nhân  ", "description": "Ghi chú"},
    )
    assert response.status_code == 201
    collection = response.json()
    assert collection["name"] == "Cá nhân"
    collection_id = collection["id"]

    assert client.get(f"/collections/{collection_id}").status_code == 200
    updated = client.patch(
        f"/collections/{collection_id}", json={"name": "Công việc"}
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Công việc"

    listed = client.get("/collections?limit=1&offset=0")
    assert listed.status_code == 200
    assert listed.json()["total"] == 1
    assert listed.json()["items"][0]["id"] == collection_id

    assert client.delete(f"/collections/{collection_id}").status_code == 204
    assert client.get(f"/collections/{collection_id}").status_code == 404

    invalid_create = client.post("/collections", json={"name": " "})
    assert invalid_create.status_code == 422
    assert invalid_create.json()["detail"] == "Dữ liệu gửi lên không hợp lệ"

    too_long_name = client.post("/collections", json={"name": "x" * 151})
    assert too_long_name.status_code == 422
    assert too_long_name.json()["detail"] == "Dữ liệu gửi lên không hợp lệ"

    invalid_update = client.patch("/collections/1", json={"name": "x" * 151})
    assert invalid_update.status_code == 422


def test_other_users_collection_is_hidden_and_not_mutable(api):
    client, engine, user_ids, active_user_id = api
    with Session(engine) as db:
        collection = Collection(user_id=user_ids[1], name="Riêng tư")
        db.add(collection)
        db.commit()
        collection_id = collection.id

    assert client.get("/collections").json()["total"] == 0
    assert client.get(f"/collections/{collection_id}").status_code == 404
    assert (
        client.patch(
            f"/collections/{collection_id}", json={"name": "Sửa trái phép"}
        ).status_code
        == 404
    )
    assert client.delete(f"/collections/{collection_id}").status_code == 404

    active_user_id["value"] = user_ids[1]
    assert client.get(f"/collections/{collection_id}").status_code == 200


def test_deleting_collection_deletes_its_notes(api):
    client, engine, user_ids, _ = api
    with Session(engine) as db:
        collection = Collection(user_id=user_ids[0], name="Có ghi chú")
        db.add(collection)
        db.flush()
        note = Note(collection_id=collection.id, title="Sẽ bị xóa")
        db.add(note)
        db.commit()
        collection_id = collection.id
        note_id = note.id

    response = client.delete(f"/collections/{collection_id}")
    assert response.status_code == 204
    with Session(engine) as db:
        assert db.scalar(select(Note).where(Note.id == note_id)) is None
