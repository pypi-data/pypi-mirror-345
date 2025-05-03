from typing import Any, Literal
from octostar_streamlit.core.method_call import MethodCall

OntologyApiMethod = Literal[
    "cancelQueries",
    "getAvailableOntologies",
    "getWorkspaceRelationshipRecords",
    "clearRelationshipCache",
    "getConnectedEntities",
    "getConceptByName",
    "getConcepts",
    "getEntity",
    "getOntologyName",
    "getRelationshipCount",
    "getConceptForEntity",
    "getRelationshipsForEntity",
    "sendQuery",
    "sendQueryT",
    "getSysInheritance",
    "subscribe",
    "consistentUUID",
]


class OntologyMethodCall(MethodCall):
    service: Literal["ontology"] = "ontology"
    method: OntologyApiMethod
    params: Any
