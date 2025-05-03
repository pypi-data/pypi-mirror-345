from typing import Any, Dict, List, Union, Optional
from octostar_streamlit.core.desktop.params import (
    AddCommentParams,
    AddWatchIntentParams,
    ApplyTagParams,
    CallAppServiceParams,
    ClearToastParams,
    CloseContextMenuParams,
    CloseTabParams,
    ConnectParams,
    CopyParams,
    CreateWorkspaceParams,
    DeleteParams,
    DeployAppParams,
    ExportParams,
    GetActiveWorkspaceParams,
    GetAttachmentParams,
    GetAvailableTagsParams,
    GetFilesTreeParams,
    GetPastContextParams,
    GetSchemaItemsParams,
    GetStylerParams,
    GetTagsParams,
    GetTemplateParams,
    GetWorkspaceItemsParams,
    GetWorkspacePermissionParams,
    ImportItemsParams,
    ImportZipParams,
    OpenContextMenuParams,
    OpenParams,
    RemoveCommentParams,
    RemoveTagParams,
    RemoveWatchIntentParams,
    SaveFileParams,
    SaveParams,
    SearchResultsParams,
    SearchXperienceParams,
    ShowConfirmParams,
    ShowCreateEntityFormParams,
    ShowProgressParams,
    ShowTabParams,
    ShowToastParams,
    UndeployAppParams,
    UpdateTagParams,
)
from octostar_streamlit.core.entities import (
    AttachmentType,
    CustomTemplate,
    Entity,
    OsTag,
    OsWorkspaceEntity,
    Styler,
    StylerOption,
    UserProfile,
    Whoami,
    Workspace,
    WorkspaceIdHost,
    WorkspaceItem,
    WorkspacePermission,
)
from octostar_streamlit.core.desktop.method_call import (
    DesktopApiMethod,
    DesktopMethodCall,
)
from octostar_streamlit.core.streamlit_executor import StreamlitMethodExecutor
from octostar_streamlit import _component_func


# TODO: provide a way to specify params as optional or required
def call_desktop_api_method(method: DesktopApiMethod, params: Any, key=None, subscribe=None) -> Any:
    call = DesktopMethodCall(service="desktop", method=method, params=params)
    value = StreamlitMethodExecutor(
        method_call=call, fn=_component_func, key=key, subscribe=subscribe
    ).execute()
    return value


def refresh(key=None) -> None:
    return call_desktop_api_method("refresh", None, key)


# def open_workspace(params: OpenWorkspaceParams, key=None) -> None:
def open_workspace(params: Union[WorkspaceIdHost, WorkspaceItem], key=None) -> None:
    return call_desktop_api_method("openWorkspace", params, key)

def close_workspace(params: Union[WorkspaceIdHost, WorkspaceItem], key=None) -> None:
    return call_desktop_api_method("closeWorkspace", params, key)

# TODO: Don't see anyone using this, need examples to test it
def get_paste_context(params: GetPastContextParams, key=None) -> List[Entity]:
    return call_desktop_api_method("getPasteContext", params, key)

def get_active_workspace(
    params: GetActiveWorkspaceParams=GetActiveWorkspaceParams(), key=None
) -> Union[str, None]:
    return call_desktop_api_method("getActiveWorkspace", params, key)

def set_active_workspace(params: WorkspaceIdHost, key=None) -> None:
    return call_desktop_api_method("setActiveWorkspace", params, key)

def copy(params: CopyParams, key=None) -> None:
    return call_desktop_api_method("copy", params, key)


def list_workspaces(key=None) -> List[WorkspaceItem]:
    return call_desktop_api_method("listAllWorkspaces", None, key)

def get_open_workspaces(key=None) -> Optional[List[Workspace]]:
    result = call_desktop_api_method("getOpenWorkspaces", None, key, subscribe="onOpenWorkspacesChanged")
    if result is None:
        return None
    return [Workspace(**v) for v in result]

def get_open_workspace_ids(key=None) -> Optional[List[str]]:
    result = call_desktop_api_method("getOpenWorkspaceIds", None, key, subscribe="onOpenWorkspaceIdsChanged")
    return result

def on_workspace_changed(uuid: str, key=None) -> Optional[Workspace]:
    result = call_desktop_api_method("onWorkspaceChanged", uuid, key)
    if result is None:
        return None
    return Workspace(**result)

def on_workspace_item_changed(uuid: str, key=None) -> Optional[Entity]:
    result = call_desktop_api_method("onWorkspaceItemChanged", uuid, key)
    if result is None:
        return None
    return Entity(**result)

def set_open_workspace_ids(ids: List[str], key=None) -> None:
    call_desktop_api_method("setOpenWorkspaceIds", ids, key)

def get_attachment(params: GetAttachmentParams, key=None) -> AttachmentType:
    return call_desktop_api_method("getAttachment", params, key)


def get_styler_options(key=None) -> Optional[List[StylerOption]]:
    result = call_desktop_api_method("getStylerOptions", None, key)
    if result is None:
        return None
    return [StylerOption(**v) for v in result]


def get_styler(params: GetStylerParams, key=None) -> Styler:
    return call_desktop_api_method("getStyler", params, key)


def get_workspace(
    params: Union[WorkspaceIdHost, WorkspaceItem], key=None
) -> Optional[Workspace]:
    result = call_desktop_api_method("getWorkspace", params, key)
    if result is None:
        return None
    return Workspace(**result)


def get_workspace_items(
    params: GetWorkspaceItemsParams, key=None
) -> List[WorkspaceItem]:
    return call_desktop_api_method("getWorkspaceItems", params, key)


def apply_tag(params: ApplyTagParams, key=None) -> None:
    return call_desktop_api_method("applyTag", params, key)


def remove_tag(params: RemoveTagParams, key=None) -> None:
    return call_desktop_api_method("removeTag", params, key)


def update_tag(params: UpdateTagParams, key=None) -> OsTag:
    return call_desktop_api_method("updateTag", params, key)


def get_item(params: Union[WorkspaceIdHost, WorkspaceItem], key=None) -> WorkspaceItem:
    return call_desktop_api_method("getItem", params, key)


def get_items(
    params: List[Union[WorkspaceIdHost, WorkspaceItem]], key=None
) -> List[WorkspaceItem]:
    return call_desktop_api_method("getItems", params, key)


def get_tags(params: GetTagsParams, key=None) -> List[Dict]:
    return call_desktop_api_method("getTags", params, key)


def get_available_tags(params: GetAvailableTagsParams, key=None) -> List[OsTag]:
    return call_desktop_api_method("getAvailableTags", params, key)


def get_templates(key=None) -> Optional[List[CustomTemplate]]:
    result = call_desktop_api_method("getTemplates", None, key)
    if result is None:
        return None
    return [CustomTemplate(**v) for v in result]


def get_template(params: GetTemplateParams, key=None) -> Optional[CustomTemplate]:
    result = call_desktop_api_method("getTemplate", params, key)
    if result is None:
        return None
    return CustomTemplate(**result)


def get_schema_items(params: GetSchemaItemsParams, key=None) -> List[WorkspaceItem]:
    return call_desktop_api_method("getSchemaItems", params, key)


def create_workspace(params: CreateWorkspaceParams, key=None) -> WorkspaceItem:
    return call_desktop_api_method("createWorkspace", params, key)


def connect(params: ConnectParams, key=None) -> WorkspaceItem:
    return call_desktop_api_method("connect", params, key)


def save(params: SaveParams, key=None) -> WorkspaceItem:
    return call_desktop_api_method("save", params, key)


def save_file(params: SaveFileParams, key=None) -> WorkspaceItem:
    return call_desktop_api_method("saveFile", params, key)


def import_items(params: ImportItemsParams, key=None) -> None:
    return call_desktop_api_method("import", params, key)


def import_zip(params: ImportZipParams, key=None) -> None:
    return call_desktop_api_method("importZip", params, key)


def export(params: ExportParams, key=None) -> None:
    return call_desktop_api_method("export", params, key)


def get_files_tree(params: GetFilesTreeParams, key=None) -> List[WorkspaceItem]:
    return call_desktop_api_method("getFilesTree", params, key)


def open(params: OpenParams, key=None) -> None:
    return call_desktop_api_method("open", params, key)


def delete(params: DeleteParams, key=None) -> None:
    return call_desktop_api_method("delete", params, key)


# TODO: Bring back the results listener?
# TODO: No more window.octostar.listen while using the platform-api, cannot do this:
# if st.button("🔍 Manual Entity Search"):
#     searchXperience(key='_manual_entity_link_' + entity_to_rank['contents']['label'])
# search_result = result(key='_manual_entity_link_' + entity_to_rank['contents']['label'])
def searchXperience(params: SearchXperienceParams, key=None) -> List[Entity]:
    result = call_desktop_api_method("searchXperience", params, key)
    return result if not result else [Entity(**v) for v in result]

# TODO: Bring back the results listener? enableSelection won't work without a listener
def get_search_results(params: SearchResultsParams, key=None) -> List[Entity]:
    result = call_desktop_api_method("getSearchResults", params, key)
    return result if not result else [Entity(**v) for v in result]

def show_tab(params: ShowTabParams, key=None) -> None:
    return call_desktop_api_method("showTab", params, key)


def close_tab(params: CloseTabParams, key=None) -> None:
    return call_desktop_api_method("closeTab", params, key)


def call_app_service(params: CallAppServiceParams, key=None) -> None:
    return call_desktop_api_method("callAppService", params, key)


def show_context_menu(
    params: Union[OpenContextMenuParams, CloseContextMenuParams], key=None
) -> None:
    return call_desktop_api_method("showContextMenu", params, key)


def show_toast(params: Union[str, ShowToastParams], key=None) -> None:
    if isinstance(params, str):
        params = ShowToastParams(message=params)
    return call_desktop_api_method("showToast", params, key)


def clear_toast(params: ClearToastParams, key=None) -> None:
    return call_desktop_api_method("clearToast", params, key)


def show_progress(params: ShowProgressParams, key=None) -> None:
    return call_desktop_api_method("showProgress", params, key)


def show_confirm(params: Union[str, ShowConfirmParams], key=None) -> Union[bool, None]:
    if isinstance(params, str):
        params = ShowConfirmParams(title=params)
    return call_desktop_api_method("showConfirm", params, key)


def show_file_upload(params: WorkspaceItem, key=None) -> List[WorkspaceItem]:
    return call_desktop_api_method("showFileUpload", params, key)


def show_create_entity_form(
    params: ShowCreateEntityFormParams, key=None
) -> Optional[List[OsWorkspaceEntity]]:
    result = call_desktop_api_method("showCreateEntityForm", params, key)
    if result is None:
        return None
    return [OsWorkspaceEntity(**v) for v in result]


def add_comment(params: AddCommentParams, key=None) -> Optional[Entity]:
    result = call_desktop_api_method("addComment", params, key)
    if result is None:
        return None
    return Entity(**result)


def remove_comment(params: RemoveCommentParams, key=None) -> None:
    return call_desktop_api_method("removeComment", params, key)


def add_watch_intent(params: AddWatchIntentParams, key=None) -> Optional[Entity]:
    result = call_desktop_api_method("addWatchIntent", params, key)
    if result is None:
        return None
    return Entity(**result)


def remove_watch_intent(params: RemoveWatchIntentParams, key=None) -> None:
    return call_desktop_api_method("removeWatchIntent", params, key)


def get_workspace_permission(
    params: GetWorkspacePermissionParams, key=None
) -> Optional[Dict[str, WorkspacePermission]]:
    result = call_desktop_api_method("getWorkspacePermission", params, key)
    if result is None:
        return None
    return {k: WorkspacePermission(**v) for k, v in result.items()}


def get_user(key=None) -> Optional[UserProfile]:
    result = call_desktop_api_method("getUser", None, key)
    if result is None:
        return None
    return UserProfile(**result)


def deploy_app(params: DeployAppParams, key=None) -> WorkspaceItem:
    return call_desktop_api_method("deployApp", params, key)


def undeploy_app(params: UndeployAppParams, key=None) -> WorkspaceItem:
    return call_desktop_api_method("undeployApp", params, key)


def whoami(key=None) -> Optional[Whoami]:
    result = call_desktop_api_method("whoami", None, key)
    if result is None:
        return None
    return Whoami(**result)


# Not implemented methods
# export interface Desktop extends DesktopSettings, WorkspaceChangeEmitter {
#   withProgressBar: <T>(
#     promise: Promise<T>,
#     options?: WithProgressBarOptions,
#   ) => Promise<T>;

#   getPasteContext: (options: PasteContextOptions) => Promise<Entity[]>;
#   showModalTemplate: (props: ModalTemplateProps) => Promise<void>;
# }
