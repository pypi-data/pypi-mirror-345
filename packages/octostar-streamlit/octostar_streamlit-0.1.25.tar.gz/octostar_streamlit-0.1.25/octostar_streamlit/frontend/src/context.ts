import {
  MethodCallDef,
  MethodCallHandler,
} from "./core";
import { contextApi, ContextApi } from "@octostar/platform-api";

type ContextApiBridge = ContextApi<any>;
type ContextApiMethodCall<M extends keyof ContextApiBridge, P> = MethodCallDef<"context", M, P>;

const methodCallHandler: MethodCallHandler<ContextApiBridge> = {
  getContext: () => contextApi().getContext(),
  // TODO: Decide their fate:
  subscribeToChanges: function (...params: any[]): Promise<void> {
    throw new Error("Function not implemented.");
  },
  unsubscribeFromChanges: function (...params: any[]): Promise<void> {
    throw new Error("Function not implemented.");
  }
};


export const forwardContextApiMethodCallToPlatform = <M extends keyof ContextApiBridge>(
  methodCall: ContextApiMethodCall<M, Parameters<ContextApiBridge[M]>[0]>
) => {
  const handler = methodCallHandler[methodCall.method];
  if (!handler) {
    throw new Error(`Unknown method: ${methodCall.method}`);
  }

  return handler(methodCall.params);
};
