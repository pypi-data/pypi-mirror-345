from dataclasses import dataclass
from io import FileIO
from typing import Any, Callable, Dict, List, Literal, Union, Optional

from pydantic import ConfigDict, Field
from octostar_streamlit.core.entities import (
    AttachmentResponseType,
    AttachmentType,
    ButtonProps,
    ContextMenuGroup,
    ContextMenuLabels,
    Entity,
    GraphSpec,
    IDataTransfer,
    ItemType,
    KeyValueTuple,
    OsTag,
    Relationship,
    TagAttributes,
    Workspace,
    WorkspaceItem,
    WorkspaceRecordIdentifier,
    WorkspaceRecordWithRelationships,
)
from octostar_streamlit.core.params_base_model import ParamsBaseModel


class GetActiveWorkspaceParams(ParamsBaseModel):
    prompt: bool = False


BinaryOperator = Literal['==', '!=', '>', '>=', '<', '<=', 'in', 'not in', 'regex', 'like', 'ilike']
Comparator = Union[str, int, List[Union[str, int]], None]

class QueryObjectFilterClause(ParamsBaseModel):
    col: str
    op: BinaryOperator
    val: Comparator

class ConceptFilter(ParamsBaseModel):
    concept: str
    filters: List[QueryObjectFilterClause]

class GetPastContextParams(ParamsBaseModel):
    limit1: Union[int, None]
    limit2: Union[int, None]
    record: Union[Entity, None]
    records: Union[List[Entity], None]
    query: Union[ConceptFilter, None] = None
    def model_dump(self, **kwargs):
        base_dict = super().model_dump(**kwargs)
        if self.records is not None:
            base_dict['records'] = [record.to_dict() for record in self.records]
        if self.record is not None:
            base_dict['record'] = self.record.to_dict()
        return base_dict

class CopyParams(ParamsBaseModel):
    source: WorkspaceItem
    target: WorkspaceItem


@dataclass
class GetAttachmentParamsOptions:
    path: Union[str, None] = None
    default: Union[AttachmentType, None] = None
    responseType: Union[AttachmentResponseType, None] = None


class GetAttachmentParams(ParamsBaseModel):
    entity: Entity
    options: Union[GetAttachmentParamsOptions, None] = None
    def model_dump(self, **kwargs):
        base_dict = super().model_dump(**kwargs)
        base_dict['entity'] = self.entity.to_dict()
        return base_dict

class GetStylerParams(ParamsBaseModel):
    name: str
    context: Dict


class GetWorkspaceItemsParams(ParamsBaseModel):
    os_item_name: str


class ApplyTagParams(ParamsBaseModel):
    os_workspace: str
    tag: Union[OsTag, TagAttributes]
    entity: Union[Entity, List[Entity]]
    def model_dump(self, **kwargs):
        base_dict = super().model_dump(**kwargs)
        if isinstance(self.entity, list):
            base_dict['entity'] = [record.to_dict() for record in self.entity]
        else:
            base_dict['entity'] = self.entity.to_dict()
        return base_dict

class RemoveTagParams(ApplyTagParams):
    pass


class UpdateTagParams(ParamsBaseModel):
    tag: OsTag


class GetTagsParams(Entity, ParamsBaseModel):
    pass


class GetAvailableTagsParams(ParamsBaseModel):
    entity: Entity
    workspace: Union[str, None] = None
    def model_dump(self, **kwargs):
        base_dict = super().model_dump(**kwargs)
        base_dict['entity'] = self.entity.to_dict()
        return base_dict

class GetTemplateParams(ParamsBaseModel):
    name: str
    defaultTemplate: Union[str, None] = None


class GetSchemaItemsParams(ParamsBaseModel):
    os_item_content_type: str


class CreateWorkspaceParams(ParamsBaseModel):
    name: str


class ConnectParams(ParamsBaseModel):
    relationship: Union[Relationship, str]
    from_entity: Entity
    to_entity: Entity
    os_workspace: Union[str, None] = None
    def model_dump(self, **kwargs):
        base_dict = super().model_dump(**kwargs)
        base_dict['from_entity'] = self.from_entity.to_dict()
        base_dict['to_entity'] = self.to_entity.to_dict()
        return base_dict


@dataclass
class SaveFileOptions:
    path: Union[str, None] = None


@dataclass
class SaveParamsOptions(SaveFileOptions):
    draft: Union[bool, None] = None
    saveAs: Union[bool, None] = None
    app: Union[WorkspaceItem, None] = None


class SaveParams(ParamsBaseModel):
    item: Union[
        WorkspaceItem, WorkspaceRecordIdentifier, WorkspaceRecordWithRelationships
    ]
    options: Union[SaveParamsOptions, None] = None


class SaveFileParams(ParamsBaseModel):
    item: WorkspaceItem
    file: Union[FileIO, str]
    options: Union[SaveFileOptions, None] = None


class ImportItemsParams(ParamsBaseModel):
    items: List[Any]


@dataclass
class ImportZipOptions:
    overwrite: Union[bool, None] = None
    target: Union[str, None] = None


class ImportZipParams(ParamsBaseModel):
    file: FileIO
    options: Union[ImportZipOptions, None] = None


@dataclass
class ExportOptions:
    filename: Union[str, None] = None


class ExportParams(ParamsBaseModel):
    item: Union[WorkspaceItem, List[WorkspaceItem]]
    options: Union[ExportOptions, None] = None


@dataclass
class FileTreeOptions:
    recurse: Union[bool, None] = None
    exclude_root: Union[bool, None] = None
    flat: Union[bool, None] = None
    minimal: Union[bool, None] = None
    structure: Union[bool, None] = None


class GetFilesTreeParams(ParamsBaseModel):
    workspace_or_folder: WorkspaceItem
    options: Union[FileTreeOptions, None] = None


class DesktopActionOptions(ParamsBaseModel):
    besideTabId: Union[str, None] = None
    autoSelectTab: Union[bool, None] = None
    onCloseTab: Union[Callable, None] = None
    desktopWith: Union[str, None] = Field(default=None, serialization_alias='with')
    initialState: Union[Any, None] = None


class OpenParams(ParamsBaseModel):
    records: Union[Entity, List[Entity]]
    options: Union[DesktopActionOptions, None] = None

    def model_dump(self, **kwargs):
        base_dict = super().model_dump(**kwargs)
        if isinstance(self.records, list):
            base_dict['records'] = [record.to_dict() for record in self.records]
        else:
            base_dict['records'] = self.records.to_dict()
        return base_dict


class DeleteParams(ParamsBaseModel):
    item: Union[WorkspaceRecordIdentifier, List[WorkspaceRecordIdentifier]]
    recurse: Union[bool, None] = None


@dataclass
class SearchXperienceOptionsDefaultSearchFields:
    entity_label: Union[str, None] = None
    os_textsearchfield: Union[str, None] = None


class SearchXperienceParams(ParamsBaseModel):
    taskID: Union[str, None] = None
    title: Union[str, None] = None
    defaultConcept: Union[List[str], None] = None
    disableConceptSelector: Union[bool, None] = None
    defaultSearchFields: Union[SearchXperienceOptionsDefaultSearchFields, None] = None

class BaseEntityModel(ParamsBaseModel):
    entity_id: str
    entity_type: str
    entity_label: str
    model_config = ConfigDict(extra="allow") # Permits additional fields



class OsAuditFieldsModel(ParamsBaseModel):
    os_created_by: Optional[str] = None
    os_created_at: Optional[str] = None
    os_deleted_by: Optional[str] = None
    os_deleted_at: Optional[str] = None
    os_hidden_by: Optional[str] = None
    os_hidden_at: Optional[str] = None
    os_last_updated_by: Optional[str] = None
    os_last_updated_at: Optional[str] = None


class WorkspaceItemBase(ParamsBaseModel):
    os_entity_uid: str
    os_workspace: str


class WorkspaceRecord(BaseEntityModel, WorkspaceItemBase, OsAuditFieldsModel):
    os_icon: Optional[str] = None


class WorkspaceItemModel(WorkspaceRecord):
    os_item_content: Optional[dict] = None
    os_item_content_type: Optional[str] = None
    os_parent_folder: Optional[str] = None
    os_has_attachment: Optional[bool] = None
    os_path: Optional[str] = None


class SearchFilter(ParamsBaseModel):
    label: Optional[str] = None
    entity: Optional[BaseEntityModel] = None
    query: Optional[Dict] = None # Elasticsearch QueryDslQueryContainer
    imageUrl: Optional[str] = None


class SearchResultsParams(ParamsBaseModel):
    q: Optional[str] = None
    submitButtonLabel: Optional[str] = None
    filters: Optional[List[SearchFilter]] = None
    image: Optional[WorkspaceItemModel] = None
    enableSelection: bool = False
    label: Optional[str] = None



class ShowTabParams(ParamsBaseModel):
    app: WorkspaceItem
    item: Union[WorkspaceItem, None] = None
    options: Union[DesktopActionOptions, None] = None


class CloseTabParams(ShowTabParams):
    pass


class CallAppServiceParams(ParamsBaseModel):
    service: str
    context: Dict
    options: Union[Dict, None] = None


@dataclass
class ActionContext:
    concept: Union[str, None] = None
    # Probably: Union[Union[GraphSpec, Any], None]
    graph: Union[GraphSpec, None] = None
    item: Union[WorkspaceItem, None] = None
    items: Union[List[WorkspaceItem], None] = None
    workspace: Union[Workspace, None] = None
    dataTransfer: Union[IDataTransfer, None] = None
    eventTopicPrefix: Union[str, None] = None
    then: Union[Callable, None] = None


@dataclass
class ContextMenuOptions:
    mode: Union[Literal["edit", "default"], None] = None
    groups: Union[List[ContextMenuGroup], None] = None
    labels: Union[ContextMenuLabels, None] = None
    extras: Union[List[ItemType], None] = None


class OpenContextMenuParams(ActionContext, ParamsBaseModel):
    x: int
    y: int
    openContextMenu: Union[bool, None] = None
    onCloseEmit: Union[str, None] = None
    options: Union[ContextMenuOptions, None] = None


class CloseContextMenuParams(ParamsBaseModel):
    clearContextMenu: Literal[True]


# OsNotification
class ShowToastParams(ParamsBaseModel):
    message: str
    id: Union[str, None] = None
    description: Union[str, None] = None
    level: Union[Literal["info", "success", "error", "warning"], None] = None
    placement: Union[
        Literal["top", "bottom", "topLeft", "topRight", "bottomLeft", "bottomRight"],
        None,
    ] = None


class ClearToastParams(ParamsBaseModel):
    id: str


class ShowProgressParams(ParamsBaseModel):
    key: str
    label: Union[str, None] = None
    job_type: Union[str, None] = None
    status: Union[Literal["active", "success", "exception", "normal"], None] = None


class ShowConfirmParams(ParamsBaseModel):
    title: str
    icon: Union[str, None] = None
    content: Union[str, None] = None
    okText: Union[str, None] = None
    okButtonProps: Union[ButtonProps, None] = None
    cancelText: Union[str, None] = None
    taskID: Union[str, None] = None


class ShowCreateEntityFormParams(ParamsBaseModel):
    os_workspace: str
    concept: Union[str, None] = None


@dataclass
class AddCommentParamsComment:
    os_workspace: str
    contents: str
    os_parent_uid: Union[str, None] = None
    slug: Union[str, None] = None


class AddCommentParams(ParamsBaseModel):
    about: Entity
    comment: AddCommentParamsComment
    def model_dump(self, **kwargs):
        base_dict = super().model_dump(**kwargs)
        base_dict['about'] = self.about.to_dict()
        return base_dict

class RemoveCommentParams(ParamsBaseModel):
    os_workspace: str
    comment_id: str


class Watcher(ParamsBaseModel):
    app_id: str
    app_name: str
    watcher_name: str
    const: List[KeyValueTuple]
    description: str
    file: str
    interval: str
    name: str
    params: List[KeyValueTuple]
    semantically_bound: List[str]


class AddWatchIntentParams(ParamsBaseModel):
    entity: Entity
    watcher: Watcher
    def model_dump(self, **kwargs):
        base_dict = super().model_dump(**kwargs)
        base_dict['entity'] = self.entity.to_dict()
        return base_dict

class RemoveWatchIntentParams(ParamsBaseModel):
    os_workspace: str
    intent_id: str


class GetWorkspacePermissionParams(ParamsBaseModel):
    os_workspace: List[str]


class DeployAppParams(ParamsBaseModel):
    app: WorkspaceItem


class UndeployAppParams(ParamsBaseModel):
    app: WorkspaceItem
