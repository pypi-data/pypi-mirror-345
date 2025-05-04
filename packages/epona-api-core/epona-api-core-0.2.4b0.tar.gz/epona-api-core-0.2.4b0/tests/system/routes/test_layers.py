import json

from src.epona.layers import services


def test_save_geometry(test_app_with_db, access_token, monkeypatch):
    headers = {"Authorization": f"Bearer {access_token}", "accept": "application/json"}

    payload = {
        "id_entidade": "a123456789-123",
        "entidade": "unidade",
        "geom": [-46.34, -23.45],
        "tipo_geom": "ponto"
    }

    async def save_geom_mock(*args):
        return "INSERT 0 1"
    monkeypatch.setattr(services, "save_geometry", save_geom_mock)
    resp = test_app_with_db.post(
        "/layers/save-geometry", data=json.dumps(payload), headers=headers)

    assert resp.status_code == 201


def test_get_geometrias(test_app_with_db, access_token, monkeypatch):
    headers = {"Authorization": f"Bearer {access_token}", "accept": "application/json"}
    payload = {
        "id": "b12345678-123",
        "id_entidade": "c12345678-123",
        "entidade": "entidade",
        "geom": [-46.34, -23.45],
        "tipo_geom": "ponto"
    }

    async def save_geom_mock(*args):
        return "INSERT 0 1"
    monkeypatch.setattr(services, "save_geometry", save_geom_mock)

    async def get_geom_mock(*args):
        return [payload]
    monkeypatch.setattr(services, "get_geometries", get_geom_mock)

    test_app_with_db.post("/layers/save-geometry", json=payload, headers=headers)

    resp = test_app_with_db.post("/layers/get-geometries", json=payload, headers=headers)

    assert resp.status_code == 200
