"""Prueba de integración completa del ciclo de vida."""

from __future__ import annotations

from fastapi import status


def test_full_article_lifecycle(client, api_headers):
    response = client.post(
        "/articles/",
        json={
            "title": "Lifecycle",
            "body": "Inicial",
            "tags": ["lifecycle"],
            "author": "Autor",
        },
        headers=api_headers,
    )
    assert response.status_code == status.HTTP_201_CREATED
    article_id = response.json()["id"]

    response = client.get(f"/articles/{article_id}", headers=api_headers)
    assert response.status_code == status.HTTP_200_OK

    response = client.put(
        f"/articles/{article_id}",
        json={"tags": ["lifecycle", "updated"]},
        headers=api_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    assert set(response.json()["tags"]) == {"lifecycle", "updated"}

    response = client.delete(f"/articles/{article_id}", headers=api_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = client.get(f"/articles/{article_id}", headers=api_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
