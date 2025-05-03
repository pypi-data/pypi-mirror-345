import { EntityPasteContext, SavedSearchAPIInterface, RecordData } from "@octostar/platform-types";
import {
  MethodCallDef,
  MethodCallHandler,
  None,
  nullishToUndefined,
} from "./core";
import { savedSearchApi } from "@octostar/platform-api";

type SavedSearchBridge = SavedSearchAPIInterface;
type ExtrasMethodCall<M extends keyof SavedSearchBridge, P> = MethodCallDef<"savedSearch", M, P>;

const methodCallHandler: MethodCallHandler<SavedSearchBridge> = {
    getRecordsCount: params => savedSearchApi().getRecordsCount(params.entity_id),
    getRecordsCountQuery: function (...params: any[]): Promise<number | null> {
        throw new Error("Function not implemented.");
    },
    getRecords: function (...params: any[]): Promise<RecordData | null> {
        throw new Error("Function not implemented.");
    },
    getRecordsQuery: function (...params: any[]): Promise<{ language: string; query: string; } | null> {
        throw new Error("Function not implemented.");
    },
    getSavedSearchPasteContext: function (...params: any[]): Promise<EntityPasteContext> {
        throw new Error("Function not implemented.");
    }
};


export const forwardSavedSearchApiMethodCallToPlatform = <M extends keyof SavedSearchBridge>(
  methodCall: ExtrasMethodCall<M, Parameters<SavedSearchBridge[M]>[0]>
) => {
  const handler = methodCallHandler[methodCall.method];
  if (!handler) {
    throw new Error(`Unknown method: ${methodCall.method}`);
  }

  return handler(methodCall.params);
};
