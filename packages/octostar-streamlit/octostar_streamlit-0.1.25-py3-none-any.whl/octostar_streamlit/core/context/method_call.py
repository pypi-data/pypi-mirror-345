from typing import Any, Literal

from octostar_streamlit.core.method_call import MethodCall


ContextApiMethod = Literal["getContext", "subscribeToChanges", "unsubscribeFromChanges"]


class ContextMethodCall(MethodCall):
    service: Literal["context"] = "context"
    method: ContextApiMethod
    params: Any
