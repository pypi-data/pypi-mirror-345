from typing import Any, Dict, List, Union

from altair import param
from octostar_streamlit.core.entities import (
    Concept,
    Entity,
    Inheritance,
    Relationship,
    RelationshipCountResult,
    WorkspaceRelationship,
)
from octostar_streamlit.core.ontology.method_call import (
    OntologyApiMethod,
    OntologyMethodCall,
)
from octostar_streamlit.core.ontology.params import (
    CancelQueriesParams,
    ClearRelationshipCacheParams,
    ConsistentUUIDParams,
    GetConceptByNameParams,
    GetConceptForEntityparams,
    GetConnectedEntitiesParams,
    GetEntityParams,
    GetRelationshipCountParams,
    GetRelationshipsForEntityParams,
    GetWorkspaceRelationshipRecordsParams,
    SendQueryParams,
    SendQueryTParams,
)
from octostar_streamlit.core.streamlit_executor import StreamlitMethodExecutor
from octostar_streamlit import _component_func


def call_ontology_api_method(method: OntologyApiMethod, params: Any, key=None):
    method_call = OntologyMethodCall(service="ontology", method=method, params=params)
    value = StreamlitMethodExecutor(
        method_call=method_call, fn=_component_func, key=key
    ).execute()
    return value


def cancel_queries(params: CancelQueriesParams, key=None) -> None:
    return call_ontology_api_method("cancelQueries", params, key)


def get_available_ontologies(key=None) -> List[str]:
    return call_ontology_api_method("getAvailableOntologies", None, key)


def get_workspace_relationship_records(
    params: GetWorkspaceRelationshipRecordsParams, key=None
) -> List[WorkspaceRelationship]:
    result = call_ontology_api_method("getWorkspaceRelationshipRecords", params, key)
    return [WorkspaceRelationship(**record) for record in result]


def clear_relationship_cache(params: ClearRelationshipCacheParams, key=None) -> None:
    return call_ontology_api_method("clearRelationshipCache", params, key)


def get_connected_entities(
    params: GetConnectedEntitiesParams, key=None
) -> List[Entity]:
    result = call_ontology_api_method("getConnectedEntities", params, key)
    return [Entity(**entity) for entity in result]


def get_concept_by_name(
    params: GetConceptByNameParams, key=None
) -> Union[Concept, None]:
    result = call_ontology_api_method("getConceptByName", params, key)
    if result is None:
        return None
    return Concept(**result)


def get_concepts(key=None) -> Dict[str, Concept]:
    result = call_ontology_api_method("getConcepts", None, key)
    return {key: Concept(**value) for key, value in result.items()}


def get_entity(params: GetEntityParams, key=None) -> Entity:
    result = call_ontology_api_method("getEntity", params, key)
    return Entity(**result)


def get_entity_by_id(entity_id: str, entity_type: str, refresh: bool = False, key=None) -> Entity:
    params = GetEntityParams(entity=Entity(entity_id=entity_id, entity_type=entity_type, entity_label=''), refresh=refresh)
    return get_entity(params=params, key=key)

def get_ontology_name(key=None) -> str:
    return call_ontology_api_method("getOntologyName", None, key)


def get_relationship_count(
    params: GetRelationshipCountParams, key=None
) -> RelationshipCountResult:
    result = call_ontology_api_method("getRelationshipCount", params, key)
    return RelationshipCountResult(**result)


def get_concept_for_entity(
    params: GetConceptForEntityparams, key=None
) -> Union[Concept, None]:
    result = call_ontology_api_method("getConceptForEntity", params, key)
    if result is None:
        return None
    return Concept(**result)


def get_relationships_for_entity(
    params: GetRelationshipsForEntityParams, key=None
) -> List[Relationship]:
    result = call_ontology_api_method("getRelationshipsForEntity", params, key)
    return [Relationship(**relationship) for relationship in result]


def send_query(params: SendQueryParams, key=None) -> List[Any]:
    return call_ontology_api_method("sendQuery", params, key)


def send_query_t(params: SendQueryTParams, key=None) -> List[Any]:
    return call_ontology_api_method("sendQueryT", params, key)

def get_sys_inheritance(key=None) -> List[Inheritance]:
    result = call_ontology_api_method("getSysInheritance", None, key)
    return [Inheritance(**inheritance) for inheritance in result]


# TODO: implement subscribe


def consistent_uuid(params: ConsistentUUIDParams, key=None) -> str:
    return call_ontology_api_method("consistentUUID", params, key)
