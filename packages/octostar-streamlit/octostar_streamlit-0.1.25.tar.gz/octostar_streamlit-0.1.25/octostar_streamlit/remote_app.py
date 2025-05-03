from typing import Any, Dict

from octostar_streamlit import _component_func
from octostar_streamlit.core.remote_app.method_call import (
    RemoteAppApiMethod,
    RemoteAppMethodCall,
)
from octostar_streamlit.core.remote_app.params import (
    SubscribeToContextParams,
    UbsubscribeFromContextParams,
)
from octostar_streamlit.core.streamlit_executor import StreamlitMethodExecutor


def call_remote_app_api_method(method: RemoteAppApiMethod, params: Any, key=None):
    call = RemoteAppMethodCall(service="remoteApp", method=method, params=params)
    value = StreamlitMethodExecutor(
        method_call=call, fn=_component_func, key=key
    ).execute()

    return value


def subscribe_to_context(id: str, key=None) -> Dict:
    if key is None:
        key = id

    return call_remote_app_api_method(
        "subscribeToContext", params=SubscribeToContextParams(id=id), key=key
    )


def unsubscribe_from_context(id: str, key=None) -> None:
    return call_remote_app_api_method(
        "unsubscribeFromContext", params=UbsubscribeFromContextParams(id=id), key=key
    )


def set_transform_result(params: Any, key=None) -> None:
    return call_remote_app_api_method("setTransformResult", params=params, key=key)

def get_current_workspace_id(key=None) -> str:
    return call_remote_app_api_method("getCurrentWorkspaceId", params=None, key=key)