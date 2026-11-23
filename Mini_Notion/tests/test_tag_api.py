import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.dependencies import get_current_user
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import Collection, Note, Tag, User


@pytest.fixture
def tags_api():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        user_a = User(
            email="tags-a@gmail.com",
            password_hash="not-used",
            full_name="User A",
            role="user",
        )
        user_b = User(
            email="tags-b@gmail.com",
            password_hash="not-used",
            full_name="User B",
            role="user",
        )
        db.add_all([user_a, user_b])
        db.flush()

        tag_a = Tag(user_id=user_a.id, name="work")
        tag_b = Tag(user_id=user_b.id, name="personal")
        db.add_all([tag_a, tag_b])
        db.flush()

        collection_a = Collection(user_id=user_a.id, name="Collection A")
        collection_b = Collection(user_id=user_b.id, name="Collection B")
        db.add_all([collection_a, collection_b])
        db.flush()

        notes = [
            Note(
                collection_id=collection_a.id,
                title="Note with work tag",
                tags=[tag_a],
            ),
            Note(
                collection_id=collection_a.id,
                title="Note without tags",
            ),
        ]
        db.add_all(notes)
        db.commit()

        user_id = user_a.id
        collection_id = collection_a.id
        tag_id = tag_a.id
        user_b_id = user_b.id

    def override_get_db():
        with Session(engine) as db:
            yield db

    def override_get_current_user() -> User:
        return User(id=user_id, role="user")

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    with TestClient(app) as client:
        yield client, engine, collection_id, tag_id, user_b_id
    app.dependency_overrides.clear()
    engine.dispose()


def test_tag_crud(tags_api):
    client, _, _, _, _ = tags_api

    create_resp = client.post("/tags", json={"name": "  New Tag  "})
    assert create_resp.status_code == 201
    tag = create_resp.json()
    assert tag["name"] == "New Tag"
    new_tag_id = tag["id"]

    list_resp = client.get("/tags")
    assert list_resp.status_code == 200
    data = list_resp.json()
    assert data["total"] >= 1
    assert any(t["id"] == new_tag_id for t in data["items"])

    delete_resp = client.delete(f"/tags/{new_tag_id}")
    assert delete_resp.status_code == 204

    list_after = client.get("/tags").json()
    assert not any(t["id"] == new_tag_id for t in list_after["items"])


def test_tag_create_validation(tags_api):
    client, _, _, _, _ = tags_api

    assert client.post("/tags", json={"name": " "}).status_code == 422
    assert client.post("/tags", json={"name": "x" * 51}).status_code == 422


def test_tag_duplicate_name_conflict(tags_api):
    client, _, _, _, _ = tags_api

    client.post("/tags", json={"name": "unique"})
    resp = client.post("/tags", json={"name": "unique"})
    assert resp.status_code == 409
    assert resp.json()["detail"] == "Thẻ đã tồn tại"


def test_tag_delete_not_found(tags_api):
    client, _, _, _, _ = tags_api

    resp = client.delete("/tags/99999")
    assert resp.status_code == 404


def test_tag_isolation_between_users(tags_api):
    client, _, _, tag_a_id, _ = tags_api

    other_tags = client.get("/tags").json()["items"]
    assert len(other_tags) == 1
    assert other_tags[0]["id"] == tag_a_id

    resp = client.delete(f"/tags/{tag_a_id}")
    assert resp.status_code == 204

    resp = client.delete(f"/tags/{tag_a_id}")
    assert resp.status_code == 404


def test_tag_pagination(tags_api):
    client, _, _, _, _ = tags_api

    for i in range(15):
        client.post("/tags", json={"name": f"tag{i}"})

    page1 = client.get("/tags?limit=10&offset=0").json()
    assert page1["limit"] == 10
    assert page1["offset"] == 0
    assert len(page1["items"]) == 10

    page2 = client.get("/tags?limit=10&offset=10").json()
    assert page2["limit"] == 10
    assert page2["offset"] == 10
    assert len(page2["items"]) >= 5


def test_tag_filter_on_notes(tags_api):
    client, _, _, tag_id, _ = tags_api

    by_tag = client.get(f"/notes?tag=work").json()
    assert by_tag["total"] == 1
    assert by_tag["items"][0]["title"] == "Note with work tag"

    by_tag = client.get(f"/notes?tag=nonexistent").json()
    assert by_tag["total"] == 0


def test_add_remove_tag_to_note(tags_api):
    client, _, collection_id, tag_id, _ = tags_api

    note_resp = client.post(
        f"/collections/{collection_id}/notes",
        json={"title": "Taggable note"},
    )
    assert note_resp.status_code == 201
    note = note_resp.json()
    note_id = note["id"]
    assert note["tags"] == []

    add_resp = client.post(f"/notes/{note_id}/tags/{tag_id}")
    assert add_resp.status_code == 200
    note_with_tag = add_resp.json()
    assert len(note_with_tag["tags"]) == 1
    assert note_with_tag["tags"][0]["id"] == tag_id
    assert note_with_tag["tags"][0]["name"] == "work"

    add_again = client.post(f"/notes/{note_id}/tags/{tag_id}")
    assert add_again.status_code == 200
    assert len(add_again.json()["tags"]) == 1

    remove_resp = client.delete(f"/notes/{note_id}/tags/{tag_id}")
    assert remove_resp.status_code == 200
    note_without_tag = remove_resp.json()
    assert note_without_tag["tags"] == []

    remove_again = client.delete(f"/notes/{note_id}/tags/{tag_id}")
    assert remove_again.status_code == 200
    assert remove_again.json()["tags"] == []


def test_add_tag_to_note_not_found(tags_api):
    client, _, _, tag_id, _ = tags_api

    resp = client.post("/notes/99999/tags/1")
    assert resp.status_code == 404


def test_add_nonexistent_tag_to_note(tags_api):
    client, _, collection_id, _, _ = tags_api

    note_resp = client.post(
        f"/collections/{collection_id}/notes",
        json={"title": "Test"},
    )
    note_id = note_resp.json()["id"]

    resp = client.post(f"/notes/{note_id}/tags/99999")
    assert resp.status_code == 404


def test_add_tag_from_other_user_to_note(tags_api):
    client, engine, collection_id, _, user_b_id = tags_api

    with Session(engine) as db:
        other_tag = Tag(user_id=user_b_id, name="other-tag")
        db.add(other_tag)
        db.commit()
        other_tag_id = other_tag.id

    note_resp = client.post(
        f"/collections/{collection_id}/notes",
        json={"title": "Test"},
    )
    note_id = note_resp.json()["id"]

    resp = client.post(f"/notes/{note_id}/tags/{other_tag_id}")
    assert resp.status_code == 404