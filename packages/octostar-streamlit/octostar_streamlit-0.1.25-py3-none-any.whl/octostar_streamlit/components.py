from typing import Any, List, Optional

from octostar_streamlit.core.components.method_call import RenderComponentCall, Components
from octostar_streamlit.core.components.params import OsContextMenuParams, OsDropzoneParams
from octostar_streamlit.core.desktop.params import SearchXperienceParams
from octostar_streamlit.core.entities import Entity
from octostar_streamlit.core.streamlit_executor import StreamlitMethodExecutor
from octostar_streamlit import _component_func


def call_components_api_method(method: Components, params: Any, key=None):
    call = RenderComponentCall(service="component", method=method, params=params)
    value = StreamlitMethodExecutor(
        method_call=call, fn=_component_func, key=key
    ).execute()

    return value

def os_contextmenu(params: OsContextMenuParams, key=None) -> None:
    return call_components_api_method("OsContextMenu", params, key=key)

def os_dropzone(params: OsDropzoneParams, key=None) -> Optional[List[dict]]:
    return call_components_api_method("OsDropzone", params, key=key)

def os_searchbutton(params: SearchXperienceParams, key=None) -> Optional[List[Entity]]:
    result = call_components_api_method("SearchXperience", params, key)
    return result if not result else [Entity(**v) for v in result]
