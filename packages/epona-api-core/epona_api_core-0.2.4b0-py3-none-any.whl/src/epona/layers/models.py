
from __future__ import annotations
from tortoise import fields, models

from src.epona.common import create_suuid

class Geometria(models.Model):
    suuid = fields.CharField(primary_key=True, max_length=13, default=create_suuid())
    id_entidade = fields.CharField(max_length=13, null=False)
    entidade = fields.CharField(max_length=20, null=False)
    representacao = fields.CharField(max_length=20, null=True)
    tipo_geom = fields.CharField(max_length=20, null=False)
    zoom = fields.IntField(null=True)

    class Meta:
        table = "geometria"
