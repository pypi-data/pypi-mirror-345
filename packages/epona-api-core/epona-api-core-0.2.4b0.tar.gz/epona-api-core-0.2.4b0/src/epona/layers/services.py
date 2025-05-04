
import json
import shutil
import tempfile
from asyncpg import Record
from fastapi import UploadFile
from shapefile import Reader, Shape
from typing import List, Optional


from src.epona.settings import conn

from epona.auth.schemas import UserSchema
from .schemas import GeometriaPayloadSchema, GeometriaResponseSchema, SGLFeature


async def save_geometry(
    payload: GeometriaPayloadSchema, user: UserSchema
) -> Optional[str]:
    """
    Recebe o schema de um local, podendo ser um ponto, reta ou uma area especifica,
    e salva (save update) no banco de dados
    """
    query = (
        "UPDATE geometria "
        "SET representacao = $1, zoom = $2,"
        f"  geom = ST_SetSRID(ST_GeomFromGeoJSON('{json.dumps(payload.coords)}'), 4326) "
        "WHERE entidade=$3 AND id_entidade=$4"
        f"  AND representacao=$5 AND tipo_geom=$6"
    )
    result = await conn.execute(
        query, [
            payload.representacao,
            payload.zoom,
            payload.entidade,
            payload.id_entidade,
            payload.representacao,
            payload.tipo_geom
        ]
    )

    if result == "UPDATE 0":
        # client_id ou id?
        query = (
            "INSERT INTO geometria "
            "  (client_id, id_entidade, entidade, representacao, tipo_geom, zoom, geom) "
            f"VALUES ($1, $2, $3, $4, $5, $6, "
            f"  ST_SetSRID(ST_GeomFromGeoJSON('{json.dumps(payload.coords)}'), 4326))"
        )
        result = await conn.execute(
            query, [
                user.client_id,
                payload.id_entidade,
                payload.entidade,
                payload.representacao,
                payload.tipo_geom,
                payload.zoom
            ]
        )

    return result


async def get_geometries(
        payload: GeometriaPayloadSchema, user: UserSchema
) -> Optional[List[GeometriaResponseSchema]]:
    """
    Recebe uma entidade e retorna todas as geometrias relacionadas com essa entidade
    """
    geom_query = (
        "SELECT "
        "  id, id_entidade, entidade, representacao, tipo_geom, zoom, "
        " ST_AsGeoJSON(geom)"
        "FROM geometria WHERE entidade = $1 AND id_entidade = $2"
    )
    result = await conn.fetch_rows(geom_query, [payload.entidade, payload.id_entidade])
    geometrias = []
    for geom in result:
        geometria = GeometriaResponseSchema(**dict(geom))
        geometria.coords = json.loads(dict(geom)["st_asgeojson"])
        geometrias.append(geometria)
    return geometrias


async def delete_geometry(payload: GeometriaPayloadSchema, user: UserSchema) -> str:
    """
    Recebe o Schema de um ponto, reta ou área e deleta do banco de dados
    """
    query = (
        "DELETE FROM geometria "
        "WHERE client_id=$1 AND entidade=$2 AND id_entidade=$3 AND tipo_geom=$4"
        f"  AND representacao=$5 AND ST_Intersects(geom, ST_Buffer(ST_SetSRID("
        f"    ST_GeomFromGeoJSON('{json.dumps(payload.coords)}'), 4326), 0.001))"
    )
    return await conn.execute(
        query, [
            user.client_id,
            payload.entidade,
            payload.id_entidade,
            payload.tipo_geom,
            payload.representacao,
        ])


async def get_layer(
    entidade: str, user: UserSchema
) -> Optional[List[GeometriaResponseSchema]]:
    """
    Recebe um usuario e uma entidade e retorna todas as geometrias relacionadas
    com esse usuario
    """
    geom_query = (
        "SELECT"
        "  id, id_entidade, entidade, representacao, tipo_geom, zoom, "
        " ST_AsGeoJSON(geom)"
        "FROM geometria "
        "WHERE client_id = $1 AND entidade = $2"
    )
    result = await conn.fetch_rows(geom_query, [user.client_id, entidade])
    return response_schema(result)


def response_schema(result: Record) -> List[GeometriaResponseSchema]:
    """
    Transforma o resultado da query do banco de dados no Schema de geometrias
    """
    geometrias = []
    for geom in result:
        geometria = GeometriaResponseSchema(**dict(geom))
        geometria.coords = json.loads(dict(geom)["st_asgeojson"])
        geometrias.append(geometria)
    return geometrias


async def load_geometry(upload_file: UploadFile, user: UserSchema) -> Optional[SGLFeature]:
    tempdir = None
    try:
        tempdir = tempfile.TemporaryDirectory()
        filename = f"{tempdir.name}/{user.username}_tempfile.zip"
        with open(filename, "wb") as file:
            file.write(upload_file.file.read())
        shp = Reader(filename)
        if len(shp) != 1:
            raise ValueError("Shapefile contém mais de uma geometria")
        if shp.shapeTypeName not in ["POLYGON", "POLYLINE"]:
            raise ValueError("Geometria deve ser simples e do tipo linha ou poligono")
        geojson, geom_type = shape_to_geojson(shp.shape(0))
        geom = SGLFeature(**{
            "coords": geojson,
            "geomType": geom_type
        })
        return geom
    except ValueError as err:
        raise err
    except Exception as ex:
        raise ValueError(f"Erro desconhecido: {str(ex)}")
    finally:
        if tempdir:
            shutil.rmtree(tempdir.name)


def shape_to_geojson(shape: Shape) -> (str, str):
    geom_type = "Polygon" if shape.shapeTypeName == "POLYGON" else "LineString"
    geojson = {
        "type": "Feature",
        "geometry": {
            "type": geom_type,
            "coordinates": [],
        },
        "properties": {}
    }
    coordinates = []
    if geom_type == "Polygon":
        coordinates = [[[point[0], point[1]] for point in reversed(shape.points)]]
    elif geom_type == "LineString":
        coordinates = [[point[0], point[1]] for point in reversed(shape.points)]
    geojson["geometry"]["coordinates"] = coordinates

    return geojson, geom_type.upper()
