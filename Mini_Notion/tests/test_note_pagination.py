from datetime import datetime

import pytest
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
def notes_api():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        user_a = User(
            email="notes-a@gmail.com",
            password_hash="not-used",
            full_name="User A",
        )
        user_b = User(
            email="notes-b@gmail.com",
            password_hash="not-used",
            full_name="User B",
        )
        db.add_all([user_a, user_b])
        db.flush()
        collection_a = Collection(user_id=user_a.id, name="A")
        collection_b = Collection(user_id=user_b.id, name="B")
        tag = Tag(user_id=user_a.id, name="work")
        db.add_all([collection_a, collection_b, tag])
        db.flush()
        notes = [
            Note(
                collection_id=collection_a.id,
                title="Pinned newer",
                is_pinned=True,
                updated_at=datetime(2026, 1, 3),
            ),
            Note(
                collection_id=collection_a.id,
                title="Pinned older",
                is_pinned=True,
                updated_at=datetime(2026, 1, 2),
            ),
            Note(
                collection_id=collection_a.id,
                title="Plan newest",
                is_pinned=False,
                updated_at=datetime(2026, 1, 4),
                tags=[tag],
            ),
            Note(
                collection_id=collection_a.id,
                title="Plan older",
                is_pinned=False,
                updated_at=datetime(2026, 1, 1),
            ),
            Note(
                collection_id=collection_b.id,
                title="Other user's note",
                is_pinned=True,
                updated_at=datetime(2026, 1, 5),
            ),
        ]
        db.add_all(notes)
        db.commit()
        user_id = user_a.id
        collection_id = collection_a.id
        other_collection_id = collection_b.id
        other_note_id = notes[-1].id

    def override_get_db():
        with Session(engine) as db:
            yield db

    def override_get_current_user() -> User:
        return User(id=user_id)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    with TestClient(app) as client:
        yield client, collection_id, other_collection_id, other_note_id
    app.dependency_overrides.clear()
    engine.dispose()


def test_note_pagination_filters_before_count_and_orders_by_pin(notes_api):
    client, _, _, _ = notes_api
    response = client.get("/notes?limit=2&offset=0")
    assert response.status_code == 200
    page = response.json()
    assert page["total"] == 4
    assert page["limit"] == 2
    assert page["offset"] == 0
    assert [item["title"] for item in page["items"]] == [
        "Pinned newer",
        "Pinned older",
    ]

    second_page = client.get("/notes?limit=2&offset=2").json()
    assert [item["title"] for item in second_page["items"]] == [
        "Plan newest",
        "Plan older",
    ]


def test_note_pagination_counts_after_filters(notes_api):
    client, collection_id, _, _ = notes_api
    by_query = client.get("/notes?q=Plan&limit=1").json()
    assert by_query["total"] == 2
    assert by_query["items"][0]["title"] == "Plan newest"

    by_tag = client.get("/notes?tag=work").json()
    assert by_tag["total"] == 1
    assert by_tag["items"][0]["title"] == "Plan newest"

    by_collection = client.get(f"/notes?collection_id={collection_id}").json()
    assert by_collection["total"] == 4
    assert all(
        item["collection_id"] == collection_id
        for item in by_collection["items"]
    )


def test_note_pagination_validates_limit_and_offset(notes_api):
    client, _, _, _ = notes_api
    assert client.get("/notes?limit=0").status_code == 422
    assert client.get("/notes?limit=101").status_code == 422
    assert client.get("/notes?offset=-1").status_code == 422


def test_note_crud_and_collection_scoped_pagination(notes_api):
    client, collection_id, other_collection_id, other_note_id = notes_api

    created = client.post(
        f"/collections/{collection_id}/notes",
        json={"title": "  Tiêu đề mới  ", "body": "Nội dung"},
    )
    assert created.status_code == 201
    note = created.json()
    assert note["title"] == "Tiêu đề mới"
    assert note["body"] == "Nội dung"
    note_id = note["id"]

    assert client.get(f"/notes/{note_id}").status_code == 200
    assert client.get(f"/notes/{other_note_id}").status_code == 404
    assert (
        client.post(
            f"/collections/{other_collection_id}/notes",
            json={"title": "Không được tạo"},
        ).status_code
        == 404
    )

    updated = client.patch(
        f"/notes/{note_id}",
        json={"title": "Đã ghim", "is_pinned": True},
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "Đã ghim"
    assert updated.json()["is_pinned"] is True

    page = client.get(
        f"/collections/{collection_id}/notes?q=ghIm&limit=1&offset=0"
    )
    assert page.status_code == 200
    assert page.json()["total"] == 1
    assert page.json()["limit"] == 1
    assert page.json()["offset"] == 0
    assert page.json()["items"][0]["id"] == note_id

    assert (
        client.get(f"/collections/{other_collection_id}/notes").status_code
        == 404
    )
    assert (
        client.patch(
            f"/notes/{other_note_id}", json={"title": "Sửa trái phép"}
        ).status_code
        == 404
    )
    assert client.delete(f"/notes/{other_note_id}").status_code == 404
    assert client.delete(f"/notes/{note_id}").status_code == 204
    assert client.get(f"/notes/{note_id}").status_code == 404


def test_note_create_and_update_validation(notes_api):
    client, collection_id, _, _ = notes_api
    assert (
        client.post(
            f"/collections/{collection_id}/notes", json={"title": " "}
        ).status_code
        == 422
    )
    assert (
        client.post(
            f"/collections/{collection_id}/notes",
            json={"title": "x" * 256},
        ).status_code
        == 422
    )

    note_id = client.post(
        f"/collections/{collection_id}/notes",
        json={"title": "Tiêu đề"},
    ).json()["id"]
    assert (
        client.patch(f"/notes/{note_id}", json={"title": None}).status_code
        == 422
    )
    assert (
        client.patch(
            f"/notes/{note_id}", json={"body": "x" * 10001}
        ).status_code
        == 422
    )
