from typing import Any, Literal

from octostar_streamlit.core.method_call import MethodCall


ExtrasApiMethod = Literal["createLinkChart"]


class ExtrasMethodCall(MethodCall):
    service: Literal["extras"] = "extras"
    method: ExtrasApiMethod
    params: Any
