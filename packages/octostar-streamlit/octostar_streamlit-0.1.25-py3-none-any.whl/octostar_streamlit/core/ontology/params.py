from dataclasses import dataclass
from typing import Union
from octostar_streamlit.core.entities import Entity, Relationship
from octostar_streamlit.core.params_base_model import ParamsBaseModel


class CancelQueriesParams(ParamsBaseModel):
    context: str


class GetWorkspaceRelationshipRecordsParams(ParamsBaseModel):
    entity: Entity
    relationship: Union[str, Relationship]
    def model_dump(self, **kwargs):
        base_dict = super().model_dump(**kwargs)
        base_dict['entity'] = self.entity.to_dict()
        return base_dict

class ClearRelationshipCacheParams(ParamsBaseModel):
    entity: Entity
    relationship: Union[str, Relationship]
    def model_dump(self, **kwargs):
        base_dict = super().model_dump(**kwargs)
        base_dict['entity'] = self.entity.to_dict()
        return base_dict

class GetConnectedEntitiesParams(ParamsBaseModel):
    entity: Entity
    relationship: Union[str, Relationship]
    forceRefresh: Union[
        bool, None
    ]  # TODO: add alias to automatically convert to camelCase instead?
    def model_dump(self, **kwargs):
        base_dict = super().model_dump(**kwargs)
        base_dict['entity'] = self.entity.to_dict()
        return base_dict

class GetConceptByNameParams(ParamsBaseModel):
    conceptName: str  # TODO: add alias to automatically convert to camelCase instead?


class GetEntityParams(ParamsBaseModel):
    entity: Entity
    refresh: Union[bool, None] = None
    skipSideEffects: Union[bool, None] = (
        None  # TODO: add alias to automatically convert to camelCase instead?
    )
    def model_dump(self, **kwargs):
        base_dict = super().model_dump(**kwargs)
        base_dict['entity'] = self.entity.to_dict()
        return base_dict


class GetRelationshipCountParams(ParamsBaseModel):
    entity: Entity
    relationship: Union[str, Relationship]
    forceRefresh: Union[
        bool, None
    ]  # TODO: add alias to automatically convert to camelCase instead?
    def model_dump(self, **kwargs):
        base_dict = super().model_dump(**kwargs)
        base_dict['entity'] = self.entity.to_dict()
        return base_dict


class GetConceptForEntityparams(ParamsBaseModel):
    entity: Entity
    def model_dump(self, **kwargs):
        base_dict = super().model_dump(**kwargs)
        base_dict['entity'] = self.entity.to_dict()
        return base_dict


class GetRelationshipsForEntityParams(ParamsBaseModel):
    entity: Entity
    def model_dump(self, **kwargs):
        base_dict = super().model_dump(**kwargs)
        base_dict['entity'] = self.entity.to_dict()
        return base_dict


@dataclass
class SendQueryOptions:
    context: Union[str, None] = None
    low_priority: Union[bool, None] = None


class SendQueryParams(ParamsBaseModel):
    query: str
    options: Union[SendQueryOptions, None] = None

class SendQueryTParams(SendQueryParams):
    force_refresh: Union[bool, None] = None


class ConsistentUUIDParams(ParamsBaseModel):
    name: str
    namespace: Union[str, None] = None
