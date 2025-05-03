from typing import Any, Literal

from octostar_streamlit.core.method_call import MethodCall


RemoteAppApiMethod = Literal[
    "subscribeToContext",
    "unsubscribeFromContext",
    "getCurrentWorkspaceId",
    "subscribeToDragStart",
    # "unsubscribeFromDragStart",
    # "dropZoneRequest",
    "setTransformResult",
]


class RemoteAppMethodCall(MethodCall):
    service: Literal["remoteApp"] = "remoteApp"
    method: RemoteAppApiMethod
    params: Any
