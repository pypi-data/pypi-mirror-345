from typing import Any

# from octostar_streamlit.core.extras.method_call import ExtrasApiMethod, ExtrasMethodCall
# from octostar_streamlit.core.extras.params import CreateLinkChartParams, OsDropzoneParams
from octostar_streamlit.core.context.method_call import ContextMethodCall, ContextApiMethod
from octostar_streamlit.core.streamlit_executor import StreamlitMethodExecutor
from octostar_streamlit import _component_func


def call_context_api_method(method: ContextApiMethod, params: Any, key=None):
    call = ContextMethodCall(service="context", method=method, params=params)
    value = StreamlitMethodExecutor(
        method_call=call, fn=_component_func, key=key
    ).execute()

    return value

def get_context(key=None):
    return call_context_api_method("getContext", {}, key=key)

# TODO: Decide their fate:
def subscribe_to_changes(id: str, callback):
    raise Exception("Function not implemented.")

def unsubscribe_from_changes(id: str):
    raise Exception("Function not implemented.")