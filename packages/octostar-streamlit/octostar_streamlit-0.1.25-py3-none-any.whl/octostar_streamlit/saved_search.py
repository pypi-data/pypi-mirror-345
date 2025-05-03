from typing import Any, Optional

from octostar_streamlit.core.entities import WorkspaceItem
from octostar_streamlit.core.saved_search.method_call import SavedSearchMethodCall, SavedSearchApiMethod
from octostar_streamlit.core.saved_search.params import SavedSearchIdn
from octostar_streamlit.core.streamlit_executor import StreamlitMethodExecutor
from octostar_streamlit import _component_func


def call_saved_search_api_method(method: SavedSearchApiMethod, params: Any, key=None):
    call = SavedSearchMethodCall(service="savedSearch", method=method, params=params)
    value = StreamlitMethodExecutor(
        method_call=call, fn=_component_func, key=key
    ).execute()

    return value


def get_records_count(params: SavedSearchIdn, key=None) -> Optional[WorkspaceItem]:
    return call_saved_search_api_method("getRecordsCount", params, key=key)
