import { WorkspaceItem } from "@octostar/platform-types";

export type MethodCallHandler<T> = {
  [K in keyof T]: (
    ...params: any[]
  ) => T[K] extends (...args: any) => infer R ? R : never;
};

export type None = null;

export const isWorkspaceItem = (value: unknown): value is WorkspaceItem => {
  return typeof value === "object" && value !== null && "os_workspace" in value;
};

export const isIdHost = (value: unknown): value is { id: string } => {
  return (
    typeof value === "object" &&
    value !== null &&
    "id" in value &&
    Object.keys(value).length === 1
  );
};

export const isNullish = (value: unknown): value is None => value === null || value === undefined;

export const nullishToUndefined = <T>(value: T | None): T | undefined =>
  value ?? undefined;

export type MethodCallDef<S, M, P> = {
  service: S;
  method: M;
  params: P;
};
