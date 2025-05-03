import {
  desktopApi,
  EnsureMethodsReturnPromise,
  remoteAppApi,
} from "@octostar/platform-api";
import { Callback, RemoteAppApi } from "@octostar/platform-types";
import { MethodCallDef, MethodCallHandler } from "./core";

export type RemoteAppMethodCall<M, P> = MethodCallDef<"remoteApp", M, P>;

export type RemoteAppBridge = EnsureMethodsReturnPromise<
  Omit<
    RemoteAppApi,
    "subscribeToDragStart" | "unsubscribeFromDragStart" | "dropZoneRequest"
  > & {
    getCurrentWorkspaceId: () => Promise<string|undefined>;
  }
>;

export const methodCallHandler: MethodCallHandler<RemoteAppBridge> = {
  subscribeToContext: async (
    params: { id: string },
    onContextChangeCallback: Callback<unknown>
  ): Promise<void> => {
    await remoteAppApi().subscribeToContext(params.id, onContextChangeCallback);
  },

  unsubscribeFromContext: async (params: { id: string }): Promise<void> => {
    await remoteAppApi().unsubscribeFromContext(params.id);
  },

  setTransformResult: async (args: any[]): Promise<void> => {
    await remoteAppApi().setTransformResult(args);
  },

  getCurrentWorkspaceId: () => desktopApi().getActiveWorkspace(true),
};

export const forwardRemoteAppApiMethodCallToPlatform = (
  methodCall: RemoteAppMethodCall<keyof RemoteAppBridge, unknown>
) => {
  const handler = methodCallHandler[methodCall.method];
  if (!handler) {
    throw new Error(`Unknown method: ${methodCall.method}`);
  }

  return handler(methodCall.params);
};
