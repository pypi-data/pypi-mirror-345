"""
Entities accepted or returned by the desktop API methods.

In most cases the entities are dataclasses so they have the following properties:
- Can be constructed with keyword arguments without pydantic validation;
- When used with pydantic BaseModel become validated models (default behavior of pydantic with stdlib dataclasses);
More: https://docs.pydantic.dev/latest/concepts/dataclasses/.

Occasionally entities are subclasses of ParamsBaseModel.
It is to cover the cases when we need to pass an entity as a parameter to the desktop API method.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Union
from octostar_streamlit.core.params_base_model import ParamsBaseModel

class WorkspaceIdHost(ParamsBaseModel):
    id: str

# TODO: Look into consolidating this and WorkspaceItemModel
WorkspaceItem = Dict

WorkspaceItems = List[WorkspaceItem]

WorkspaceIdentifier = Union[WorkspaceIdHost, WorkspaceItem]


# TODO: Look into consolidating Entity and BaseEntityModel
# We need the entities returned from the SDK to be able to funnel back into let’s say createLinkChart in a lossless fashion.
@dataclass(init=False)
class Entity:
    entity_id: str
    entity_type: str
    entity_label: str
    additional_properties: dict = field(default_factory=dict)

    def __init__(self, entity_id: str, entity_type: str, entity_label: str, **kwargs):
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.entity_label = entity_label
        # Capture any additional fields
        self.additional_properties = kwargs

    def to_dict(self):
        # Convert the instance back to a dictionary and flatten additional properties
        base_dict = {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "entity_label": self.entity_label,
        }
        return {**base_dict, **self.additional_properties}

OsTag = Dict


@dataclass
class TagInfo:
    tag: str
    os_workspace: str
    count: int
    sample: List[Entity]
    entity: OsTag


@dataclass
class WorkspaceRecordInfo:
    concept: str
    count: int
    max_last_updated: str
    entities: List[Entity]


WorkspaceRecords = Dict[str, WorkspaceRecordInfo]


# This class is used as enum
class WorkspacePermissionValue:
    NONE = 0
    Read = 1
    Write = 2
    Admin = 4


@dataclass
class WorkspacePermission:
    value: WorkspacePermissionValue
    label: str


@dataclass
class Workspace:
    workspace: WorkspaceItem
    items: WorkspaceItems
    os_flags: int
    workspace_records: Union[WorkspaceRecords, None] = None
    tags: Union[List[TagInfo], None] = None
    permission: Union[WorkspacePermission, None] = None
    # FIXME: consider implementing automaticacasting to snake_case
    isActive: Union[bool, None] = None


@dataclass
class Colorful:
    color: Union[str, None] = None


@dataclass
class RequiredTagAttributes:
    os_workspace: str
    os_item_name: str


@dataclass
class TagAttributes(Colorful, RequiredTagAttributes):
    # os_workspace: str
    # os_item_name: str
    group: Union[str, None] = None
    order: Union[int, None] = None


AttachmentType = Any

AttachmentResponseType = Literal["text", "blob", "arrayBuffer", "json", "url"]


@dataclass
class StylerOption:
    name: str
    description: str


Styler = Dict

TemplateType = Literal["nunjucks", "javascript"]

TemplateVariant = Literal["antd"]


@dataclass
class TemplateMetadataRequiredFields:
    name: str
    description: str
    concepts: List[str]
    type: TemplateType
    variant: TemplateVariant
    parameterNames: List[str]


@dataclass
class TemplateMetadataOptionalFields:
    blurhash: Union[str, None] = None
    style: Union[Dict, None] = None
    rendersMultipleRecords: Union[bool, None] = None


@dataclass
class TemplateMetadata(TemplateMetadataOptionalFields, TemplateMetadataRequiredFields):
    pass


@dataclass
class CustomTemplateRequiredFields:
    template: str


@dataclass
class CustomTemplate(TemplateMetadata, CustomTemplateRequiredFields):
    pass


@dataclass
class Relationship:
    key: str
    concept: str
    target_concept: str
    relationship_name: str
    inverse_name: str
    source_properties: str
    target_properties: str
    mapping_name: str
    additional_properties: str
    mapping_query: str
    tables: str
    mapping_json: str
    is_inverse: int
    is_mtm: int
    transitivity: int
    datasource_id: str
    sort_order: int
    description: Union[str, None] = None


@dataclass
class WorkspaceRecordIdentifier:
    entity_type: str
    os_entity_uid: str
    os_workspace: str


@dataclass
class WorkspaceRecordWithRelationships:
    entity: WorkspaceItem
    relationship_name: Union[str, None] = None
    relationships: Union[List[Dict], None] = None


EdgeSpec = Dict


@dataclass
class GraphSpec:
    nodes: List[Entity]
    edges: List[EdgeSpec]
    workspace_item: Union[Entity, None] = None


IDataTransfer = Dict


ContextMenuGroup = Literal[
    "add",
    "addto",
    "edit",
    "transform",
    "general",
    "open",
    "danger",
    "tags",
]

ContextMenuLabels = Dict[ContextMenuGroup, str]

ItemType = Dict


ButtonProps = Dict


class OsWorkspaceEntity(Entity, WorkspaceRecordIdentifier):
    pass


# [key: string, value: any]
KeyValueTuple = List


@dataclass
class UserProfile:
    firstName: str
    lastName: str
    email: str
    username: str


@dataclass
class Whoami:
    async_channel: str
    os_jwt: str
    username: str
    is_superuser: bool
    roles: List[str]
    timbr_roles: List[str]
    email: Union[str, None] = None


@dataclass
class OsAuditFields:
    os_created_by: Union[str, None] = None
    os_created_at: Union[str, None] = None
    os_deleted_by: Union[str, None] = None
    os_deleted_at: Union[str, None] = None
    os_hidden_by: Union[str, None] = None
    os_hidden_at: Union[str, None] = None
    os_last_updated_by: Union[str, None] = None
    os_last_updated_at: Union[str, None] = None


@dataclass
class WorkspaceItemModel:
    os_item_name: str
    os_item_type: str


@dataclass
class WorkspaceItemBase(WorkspaceItemModel):
    os_entity_uid: str
    os_workspace: str


@dataclass
class WorkspaceRelationshipRequiredFields:
    os_entity_uid_from: str
    os_entity_uid_to: str
    os_entity_type_from: str
    os_entity_type_to: str
    os_relationship_name: str


@dataclass
class WorkspaceRelationship(
    OsAuditFields, WorkspaceRelationshipRequiredFields, WorkspaceItemBase
):
    pass


@dataclass
class Property:
    concept: str
    property_name: str
    property_type: str


@dataclass
class Tag:
    tag_name: str
    tag_value: str


@dataclass
class Concept:
    concept_name: str
    parents: List[str]
    relationships: List[Relationship]
    columns: List[str]
    archetype: Dict
    tags: List[Tag]
    labelKeys: List[str]
    allLabelKeys: List[str]
    properties: Union[List[Property], None] = None
    allProperties: Union[List[Property], None] = None


@dataclass
class RelationshipCountResult:
    count: int
    expired: Union[bool, None] = None


@dataclass
class Inheritance:
    base_concept: str
    derived_concept: str
