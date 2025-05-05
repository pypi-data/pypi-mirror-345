from typing import List

from pydantic import BaseModel, ConfigDict


class EntityMirrorAcrossEdge(BaseModel):
    """The response from the `EntityMirrorAcrossEdge` endpoint."""

    entity_ids: List[str]

    model_config = ConfigDict(protected_namespaces=())
