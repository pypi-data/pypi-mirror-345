
from typing import Optional
from pydantic import BaseModel


class GeometriaPayloadSchema(BaseModel):
    id_entidade: str
    entidade: str
    coords: Optional[dict]
    representacao: Optional[str]
    tipo_geom: Optional[str]
    zoom: Optional[int]


class GeometriaResponseSchema(GeometriaPayloadSchema):
    id: str


class SGLFeature(BaseModel):
    id: Optional[str]
    coords: Optional[dict]
    entity: Optional[str]
    entityId: Optional[str]
    geomType: Optional[str]
    representation: Optional[str]
    zoom: Optional[str]
