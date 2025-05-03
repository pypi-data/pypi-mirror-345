import { desktopApi } from "@octostar/platform-api";
import {
  AppServiceCallOptions,
  AttachmentType,
  ContextMenuGroup,
  ContextMenuLabels,
  Desktop,
  DesktopActionOptions,
  DesktopStylerContext,
  Entity,
  ExportOptions,
  FileTreeOptions,
  GetAttachmentOptions,
  IDataTransfer,
  ImportZipOptions,
  OsTag,
  PasteContextOptions,
  Relationship,
  SearchProps,
  SaveOptions,
  TagAttributes,
  TagInfo,
  Watcher,
  WorkspaceItem,
  WorkspacePermissionValue,
  WorkspaceRecordIdentifier,
  WorkspaceRecordInfo,
  WorkspaceRecordWithRelationships,
  Callback,
  Unsubscribe,
  Workspace,
} from "@octostar/platform-types";
import {
  MethodCallDef,
  MethodCallHandler,
  None,
  isIdHost,
  isNullish,
  nullishToUndefined,
} from "./core";
import { Streamlit } from "streamlit-component-lib";

type SearchPropsExtended = SearchProps & { enableSelection: boolean };

type DesktopApiMethodCall<M extends keyof Desktop, P> = MethodCallDef<
  "desktop",
  M,
  P
>;

type InternalWorkspaceItemIdentifier = { id: string } | WorkspaceItem;

type BridgedDesktop = Omit<
  Desktop,
  | "withProgressBar"
  | "showModalTemplate"
  | "delete_workspace_records"
  | "delete_local_concept_records"
  | "showCreateRelationsDialog"
  | "getFocusList"
  | "addToFocusList"
  | "removeFromFocusList"
  | "getOntology" // This just returns BabyOntologyAPI, Omitted
  // TODO: The following should be private properties on the DesktopAPI implementation, not in our interface
  | "handleFailedWorkspace"
  | "failedWorkspaceModal"
  | "workspaceStore"
>;

function getCallback(callDescriptor: string) {
  return function (value: any) {
    console.log(`StreamlitSDK: Value changed for ${callDescriptor}`, value);
    Streamlit.setComponentValue(value);
  }
}
let persistedResult: Promise<any> | null = null;
let subscribedToFutureResults: false|Promise<Unsubscribe> = false;
// Attach cleanup when the component is removed
window.addEventListener("unload", () => {
  if (subscribedToFutureResults) {
    subscribedToFutureResults.then(cleanup => cleanup()).finally(() => {
      subscribedToFutureResults = false;
    });
  }
});

const methodCallHandler: MethodCallHandler<BridgedDesktop> = {
  refresh: () => desktopApi().refresh(),

  openWorkspace: (params: InternalWorkspaceItemIdentifier) => desktopApi().openWorkspace(isIdHost(params) ? params.id : params),

  getActiveWorkspace: (params: { prompt: boolean; }) => desktopApi().getActiveWorkspace(params.prompt),

  getPasteContext: (params: PasteContextOptions) => desktopApi().getPasteContext(params),

  setActiveWorkspace: (params: { id: string; }) => desktopApi().setActiveWorkspace(params.id),

  closeWorkspace: (params: InternalWorkspaceItemIdentifier) => desktopApi().closeWorkspace(isIdHost(params) ? params.id : params),

  copy: (params: { source: WorkspaceItem; target: WorkspaceItem; }) => desktopApi().copy(params.source, params.target),

  listAllWorkspaces: () => desktopApi().listAllWorkspaces(),

  getOpenWorkspaces: () => desktopApi().getOpenWorkspaces(),

  getOpenWorkspaceIds: () => desktopApi().getOpenWorkspaceIds(),

  onOpenWorkspaceIdsChanged: (callback: Callback<string[]>): Promise<Unsubscribe> =>  desktopApi().onOpenWorkspaceIdsChanged(callback),

  setOpenWorkspaceIds: (params: string[]) => desktopApi().setOpenWorkspaceIds(params),

  onOpenWorkspacesChanged: (callback: Callback<Workspace[]>) => desktopApi().onOpenWorkspacesChanged(callback),

  onWorkspaceChanged: (uuid: string): Promise<Unsubscribe> => {
    subscribedToFutureResults = desktopApi().onWorkspaceChanged(uuid, getCallback(`onWorkspaceChanged:${uuid}`));
    return subscribedToFutureResults;
  },
  onWorkspaceItemChanged: (uuid: string): Promise<Unsubscribe> => {
    subscribedToFutureResults = desktopApi().onWorkspaceItemChanged(uuid, getCallback(`onWorkspaceItemChanged:${uuid}`));
    return subscribedToFutureResults;
  },
  getAttachment: (params: {
    entity: Entity;
    options: GetAttachmentOptions<AttachmentType> | None;
  }) => desktopApi().getAttachment(params.entity, nullishToUndefined(params.options)),

  getStylerOptions: () => desktopApi().getStylerOptions(),

  getStyler: (params: { name: string; context: DesktopStylerContext; }) => desktopApi().getStyler(params.name, params.context),

  getWorkspace: (params: InternalWorkspaceItemIdentifier) => desktopApi().getWorkspace(isIdHost(params) ? params.id : params),

  getWorkspaceItems: (params: { os_item_name: string; }) => desktopApi().getWorkspaceItems(params.os_item_name),

  applyTag: (params: {
    os_workspace: string;
    tag: OsTag | TagAttributes;
    entity: Entity | Entity[];
  }) => desktopApi().applyTag(params.os_workspace, params.tag, params.entity),

  removeTag: (params: {
    os_workspace: string;
    tag: OsTag | TagAttributes;
    entity: Entity | Entity[];
  }) => desktopApi().removeTag(params.os_workspace, params.tag, params.entity),

  updateTag: (params: { tag: OsTag; }) => desktopApi().updateTag(params.tag),

  getItem: (params: InternalWorkspaceItemIdentifier) => desktopApi().getItem(isIdHost(params) ? params.id : params),

  getItems: (params: InternalWorkspaceItemIdentifier[]) => desktopApi().getItems(
    params.map((item) => (isIdHost(item) ? item.id : item))
  ),

  getTags: (params: Entity) => desktopApi().getTags(params),

  getAvailableTags: (params: { entity: Entity; workspace: string | None; }) => desktopApi().getAvailableTags(
    params.entity,
    nullishToUndefined(params.workspace)
  ),

  getTemplates: () => desktopApi().getTemplates(),

  getTemplate: (params: { name: string; defaultTemplate: string | None; }) => desktopApi().getTemplate(
    params.name,
    nullishToUndefined(params.defaultTemplate)
  ),

  getSchemaItems: (params: { os_item_content_type: string; }) => desktopApi().getSchemaItems(params.os_item_content_type),

  createWorkspace: (params: { name: string; }) => desktopApi().createWorkspace(params.name),

  connect: (params: {
    relationship: string | Relationship;
    from_entity: Entity;
    to_entity: Entity;
    os_workspace: string | None;
  }) => desktopApi().connect(
    params.relationship,
    params.from_entity,
    params.to_entity,
    nullishToUndefined(params.os_workspace)
  ),

  save: (params: {
    item: WorkspaceItem |
    WorkspaceRecordIdentifier |
    WorkspaceRecordWithRelationships;
    options: SaveOptions | None;
  }) => desktopApi().save(params.item, nullishToUndefined(params.options)),

  saveFile: (params: {
    item: WorkspaceItem;
    file: string | File;
    options: SaveOptions | None;
  }) => desktopApi().saveFile(
    params.item,
    params.file,
    nullishToUndefined(params.options)
  ),

  import: (params: { items: any[]; }) => desktopApi().import(params.items),

  importZip: (params: { file: File; options: ImportZipOptions | None; }) => desktopApi().importZip(params.file, nullishToUndefined(params.options)),

  export: (params: {
    item: WorkspaceItem | WorkspaceItem[];
    options: ExportOptions | None;
  }) => desktopApi().export(params.item, nullishToUndefined(params.options)),

  getFilesTree: (params: {
    workspace_or_folder: WorkspaceItem;
    options: FileTreeOptions | None;
  }) => desktopApi().getFilesTree(
    params.workspace_or_folder,
    nullishToUndefined(params.options)
  ),

  open: (params: {
    records: Entity | Entity[];
    options: DesktopActionOptions | None;
  }) => {
    if (!persistedResult) {
      persistedResult = desktopApi().open(params.records, nullishToUndefined(params.options));
    }
    return persistedResult;
  },

  delete: (params: {
    item: WorkspaceRecordIdentifier | WorkspaceRecordIdentifier[];
    recurse: boolean | None;
  }) => desktopApi().delete(params.item, nullishToUndefined(params.recurse)),

  searchXperience: (params: {
    taskID: string | None;
    title: string | None;
    defaultConcept: string[] | None;
    disableConceptSelector: boolean | None;
    defaultSearchFields: {
      entity_label: string | None;
      os_textsearchfield: string | None;
    } |
    None;
  }) => desktopApi().searchXperience({
    taskID: nullishToUndefined(params.taskID),
    title: nullishToUndefined(params.title),
    defaultConcept: nullishToUndefined(params.defaultConcept),
    disableConceptSelector: nullishToUndefined(params.disableConceptSelector),
    defaultSearchFields: isNullish(params.defaultSearchFields)
      ? undefined
      : {
        entity_label: nullishToUndefined(
          params.defaultSearchFields.entity_label
        ),
        os_textsearchfield: nullishToUndefined(
          params.defaultSearchFields.os_textsearchfield
        ),
      },
  }),

  getSearchResults: (params: SearchPropsExtended) => {
    if (!persistedResult || params.enableSelection) {
      persistedResult = desktopApi().getSearchResults(params, params.enableSelection);
    }
    return persistedResult;
  },

  showTab: (params: {
    app: WorkspaceItem;
    item: WorkspaceItem | None;
    options: DesktopActionOptions | None;
  }) => desktopApi().showTab({
    app: params.app,
    item: nullishToUndefined(params.item),
    options: nullishToUndefined(params.options),
  }),

  closeTab: (params: {
    app: WorkspaceItem;
    item: WorkspaceItem | None;
    options: DesktopActionOptions | None;
  }) => desktopApi().closeTab({
    app: params.app,
    item: nullishToUndefined(params.item),
    options: nullishToUndefined(params.options),
  }),

  callAppService: (params: {
    service: string;
    context: object;
    options: AppServiceCallOptions | None;
  }) => desktopApi().callAppService({
    service: params.service,
    context: params.context,
    options: nullishToUndefined(params.options),
  }),

  showContextMenu: (
    params: {
      concept: string | None;
      graph: {
        entity: WorkspaceItem;
        relationship_name: string | None;
        relatioship: Relationship | None;
      } |
      None;
      item: WorkspaceItem | None;
      items: WorkspaceItem[] | None;
      workspace: {
        workspace: WorkspaceItem;
        items: WorkspaceItem[];
        workspace_records: Record<string, WorkspaceRecordInfo> | None;
        tags: TagInfo[] | None;
        permission: { value: WorkspacePermissionValue; label: string; } |
        None;
        isActive: boolean | None;
      } |
      None;
      dataTransfer: IDataTransfer | None;
      eentTopicPrefix: string | None;
      then: (...args: any[]) => any | None;
      x: number;
      y: number;
      openContextMenu: boolean | None;
      onCloseEmit: string | None;
      options: {
        mode: "edit" | "default" | None;
        groups: ContextMenuGroup[] | None;
        labels: ContextMenuLabels | None;
        extras: any[] /* FIXME: actual type is ItemType but it is not exported */ |
        None;
      } |
      None;
    } |
    { clearContextMenu: true; }
  ) => {
    if (params && typeof params === "object" && "clearContextMenu" in params) {
      return desktopApi().showContextMenu({
        clearContextMenu: params.clearContextMenu,
      });
    }

    return desktopApi().showContextMenu({
      concept: nullishToUndefined(params.concept),
      graph: nullishToUndefined(params.graph),
      item: nullishToUndefined(params.item),
      items: nullishToUndefined(params.items),
      workspace: isNullish(params.workspace)
        ? undefined
        : {
          workspace: params.workspace.workspace,
          items: params.workspace.items,
          workspace_records: nullishToUndefined(
            params.workspace.workspace_records
          ),
          tags: nullishToUndefined(params.workspace.tags),
          permission: nullishToUndefined(params.workspace.permission),
          isActive: nullishToUndefined(params.workspace.isActive),
        },
      dataTransfer: nullishToUndefined(params.dataTransfer),
      eventTopicPrefix: nullishToUndefined(params.eentTopicPrefix),
      then: nullishToUndefined(params.then),
      x: params.x,
      y: params.y,
      openContextMenu: nullishToUndefined(params.openContextMenu),
      onCloseEmit: nullishToUndefined(params.onCloseEmit),
      options: isNullish(params.options)
        ? undefined
        : {
          mode: nullishToUndefined(params.options.mode),
          groups: nullishToUndefined(params.options.groups),
          labels: nullishToUndefined(params.options.labels),
          extras: nullishToUndefined(params.options.extras),
        },
    });
  },

  showToast: (params: {
    message: string;
    id: string | None;
    description: string | None;
    level: "info" | "success" | "error" | "warning" | None;
    placement: "top" |
    "bottom" |
    "topLeft" |
    "topRight" |
    "bottomLeft" |
    "bottomRight" |
    None;
  }) => desktopApi().showToast({
    message: params.message,
    id: nullishToUndefined(params.id),
    description: nullishToUndefined(params.description),
    level: nullishToUndefined(params.level),
    placement: nullishToUndefined(params.placement),
  }),

  clearToast: (params: { id: string; }) => desktopApi().clearToast(params.id),

  showProgress: (params: {
    key: string;
    label: string | None;
    job_type: string | None;
    status: "active" | "success" | "exception" | "normal" | None;
  }) => desktopApi().showProgress({
    key: params.key,
    label: nullishToUndefined(params.label),
    job_type: nullishToUndefined(params.job_type),
    status: nullishToUndefined(params.status),
  }),

  showConfirm: (params: {
    title: string;
    icon: string | None;
    content: string | None;
    okText: string | None;
    okButtonProps: { [key: string]: any; } | None;
    cancelText: string | None;
    taskID: string | None;
  }) => desktopApi().showConfirm({
    title: params.title,
    icon: nullishToUndefined(params.icon),
    content: nullishToUndefined(params.content),
    okText: nullishToUndefined(params.okText),
    okButtonProps: nullishToUndefined(params.okButtonProps),
    cancelText: nullishToUndefined(params.cancelText),
    taskID: nullishToUndefined(params.taskID),
  }),

  showFileUpload: (params: WorkspaceItem) => desktopApi().showFileUpload(params),

  showCreateEntityForm: (params: {
    os_workspace: string;
    concept: string | None;
  }) => desktopApi().showCreateEntityForm({
    os_workspace: params.os_workspace,
    concept: nullishToUndefined(params.concept),
  }),

  addComment: (params: {
    about: Entity;
    comment: {
      os_workspace: string;
      contents: string;
      os_parent_uid: string | None;
      slug: string | None;
    };
  }) => desktopApi().addComment(params.about, {
    os_workspace: params.comment.os_workspace,
    contents: params.comment.contents,
    os_parent_uid: nullishToUndefined(params.comment.os_parent_uid),
    slug: nullishToUndefined(params.comment.slug),
  }),

  // removeComment: (params: { os_workspace: string; comment_id: string }) =>
  //   desktopApi().removeComment(params.os_workspace, params.comment_id),
  addWatchIntent: (params: { entity: Entity; watcher: Watcher; }) => desktopApi().addWatchIntent(params.entity, params.watcher),

  removeWatchIntent: (params: { os_workspace: string; intent_id: string; }) => desktopApi().removeWatchIntent(params.os_workspace, params.intent_id),

  getWorkspacePermission: (params: { os_workspace: string[]; }) => desktopApi().getWorkspacePermission(params.os_workspace),

  getUser: () => desktopApi().getUser(),

  deployApp: (params: { app: WorkspaceItem; }) => desktopApi().deployApp(params.app),

  undeployApp: (params: { app: WorkspaceItem; }) => desktopApi().undeployApp(params.app),

  whoami: () => desktopApi().whoami(),
  // TODO: Newer methods decide their fate
  getApp: function (...params: any[]): Promise<WorkspaceItem | undefined> {
    throw new Error("Function not implemented.");
  },
  extractEntities: function (...params: any[]): Promise<Entity[]> {
    throw new Error("Function not implemented.");
  },
  showSaveAsModal: function (...params: any[]): Promise<WorkspaceItem | undefined> {
    throw new Error("Function not implemented.");
  },
  getImages: function (...params: any[]): Promise<Entity[]> {
    throw new Error("Function not implemented.");
  },
  internalGetIconCode: function (...params: any[]): Promise<string> {
    throw new Error("Function not implemented.");
  },
  getJSONSchema: function (...params: any[]): Promise<{ schema: string; schemaUI: string; }> {
    throw new Error("Function not implemented.");
  },
  addAttachment: function (...params: any[]): void {
    throw new Error("Function not implemented.");
  },
  getConfigFiles: function (...params: any[]): Promise<WorkspaceItem[]> {
    throw new Error("Function not implemented.");
  },
  getWhitelabelingInfo: function (...params: any[]): Promise<{ OCTOSTAR_MAIN_LOGO: string; OCTOSTAR_FAVICON: string; OCTOSTAR_SPINNER: string; }> {
    throw new Error("Function not implemented.");
  },
  unzipFiles: function (...params: any[]): void {
    throw new Error("Function not implemented.");
  },
  getOsAPIClient: function (...params: any[]): Promise<any> {
    throw new Error("Function not implemented.");
  },
  getAIClient: function (...params: any[]): Promise<any> {
    throw new Error("Function not implemented.");
  },
  createPrivateWorkspace: function (...params: any[]): Promise<Workspace> {
    throw new Error("Function not implemented.");
  },
  fetchEntity: function (...params: any[]): Promise<Entity> {
    throw new Error("Function not implemented.");
  },
  search: function (...params: any[]): Promise<any> {
    throw new Error("Function not implemented.");
  },
  getImageUrl: function (...params: any[]): Promise<string> {
    throw new Error("Function not implemented.");
  }
};

export const forwardDesktopApiMethodCallToPlatform = (
  methodCall: DesktopApiMethodCall<keyof BridgedDesktop, unknown>
) => {
  const handler = methodCallHandler[methodCall.method];
  if (!handler) {
    throw new Error(`Unknown method: ${methodCall.method}`);
  }

  return handler(methodCall.params);
};
