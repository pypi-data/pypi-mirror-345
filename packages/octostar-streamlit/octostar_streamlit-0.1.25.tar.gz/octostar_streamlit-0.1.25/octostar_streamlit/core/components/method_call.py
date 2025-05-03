from typing import Any, Literal
from octostar_streamlit.core.method_call import MethodCall


Components = Literal[
    "SearchXperience",
    "OsDropzone",
    "OsContextMenu",
]

class RenderComponentCall(MethodCall):
    service: Literal["component"] = "component"
    method: Components
    params: Any
