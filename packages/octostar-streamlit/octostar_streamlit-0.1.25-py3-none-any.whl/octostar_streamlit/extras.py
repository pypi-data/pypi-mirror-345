from typing import Any, Optional

from octostar_streamlit.core.entities import WorkspaceItem
from octostar_streamlit.core.extras.method_call import ExtrasApiMethod, ExtrasMethodCall
from octostar_streamlit.core.extras.params import CreateLinkChartParams
from octostar_streamlit.core.streamlit_executor import StreamlitMethodExecutor
from octostar_streamlit import _component_func


def call_extras_api_method(method: ExtrasApiMethod, params: Any, key=None):
    call = ExtrasMethodCall(service="extras", method=method, params=params)
    value = StreamlitMethodExecutor(
        method_call=call, fn=_component_func, key=key
    ).execute()

    return value


def create_link_chart(params: CreateLinkChartParams, key=None) -> Optional[WorkspaceItem]:
    return call_extras_api_method("createLinkChart", params, key=key)
