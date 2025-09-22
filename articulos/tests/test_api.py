"""Pruebas de integración sobre los endpoints del API."""

from __future__ import annotations

from datetime import datetime

from fastapi import status


def test_create_and_get_article_via_api(client, api_headers):
    payload = {
        "title": "API",
        "body": "Contenido via API",
        "tags": ["fastapi", "crud"],
        "author": "Laura",
    }

    response = client.post("/articles/", json=payload, headers=api_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    article_id = data["id"]

    response = client.get(f"/articles/{article_id}", headers=api_headers)
    assert response.status_code == status.HTTP_200_OK
    fetched = response.json()
    assert fetched["title"] == payload["title"]


def test_list_filters_and_pagination(client, api_headers):
    for idx in range(3):
        payload = {
            "title": f"Listado {idx}",
            "body": "Contenido",
            "tags": ["tag" if idx != 1 else "otro"],
            "author": "Laura" if idx < 2 else "Pedro",
            "published_at": datetime.utcnow().isoformat(),
        }
        client.post("/articles/", json=payload, headers=api_headers)

    response = client.get("/articles/?author=Laura&limit=2", headers=api_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] >= 2
    assert len(data["items"]) <= 2


def test_update_and_delete_via_api(client, api_headers):
    payload = {
        "title": "Actualizar",
        "body": "Contenido",
        "tags": ["tag"],
        "author": "Laura",
    }

    response = client.post("/articles/", json=payload, headers=api_headers)
    article_id = response.json()["id"]

    update_payload = {"body": "Actualizado"}
    response = client.put(f"/articles/{article_id}", json=update_payload, headers=api_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["body"] == "Actualizado"

    response = client.delete(f"/articles/{article_id}", headers=api_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = client.get(f"/articles/{article_id}", headers=api_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_requires_api_key(client):
    response = client.get("/articles/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
