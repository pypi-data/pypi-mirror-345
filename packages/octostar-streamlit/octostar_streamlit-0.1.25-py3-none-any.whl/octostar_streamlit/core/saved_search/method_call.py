from typing import Any, Literal

from octostar_streamlit.core.method_call import MethodCall


SavedSearchApiMethod = Literal["getRecordsCount"]


class SavedSearchMethodCall(MethodCall):
    service: Literal["savedSearch"] = "savedSearch"
    method: SavedSearchApiMethod
    params: Any
