import { EdgeSpec, Entity, ExtrasApi } from "@octostar/platform-types";
import {
  MethodCallDef,
  MethodCallHandler,
  None,
  nullishToUndefined,
} from "./core";
import { extrasApi } from "@octostar/platform-api";

type ExtrasBridge = ExtrasApi;
type ExtrasMethodCall<M extends keyof ExtrasBridge, P> = MethodCallDef<"extras", M, P>;

const methodCallHandler: MethodCallHandler<ExtrasBridge> = {
  createLinkChart: (params: {
    path: string | None;
    name: string;
    nodes: Entity[] | None;
    edges: EdgeSpec[] | None;
    draft: boolean | None;
    os_workspace: string | None;
  }) =>
    extrasApi().createLinkChart({
      name: params.name,
      path: nullishToUndefined(params.path),
      nodes: nullishToUndefined(params.nodes),
      edges: nullishToUndefined(params.edges),
      draft: nullishToUndefined(params.draft),
      os_workspace: nullishToUndefined(params.os_workspace),
    }),
};


export const forwardExtrasApiMethodCallToPlatform = <M extends keyof ExtrasBridge>(
  methodCall: ExtrasMethodCall<M, Parameters<ExtrasBridge[M]>[0]>
) => {
  const handler = methodCallHandler[methodCall.method];
  if (!handler) {
    throw new Error(`Unknown method: ${methodCall.method}`);
  }

  return handler(methodCall.params);
};
