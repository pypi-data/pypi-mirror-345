from typing import Dict, Union
from octostar_streamlit.core.params_base_model import ParamsBaseModel

class OsDropzoneParams(ParamsBaseModel):
    label: str

class OsContextMenuParams(ParamsBaseModel):
    item: Dict
    label: Union[str, None] = None
    height: Union[str, None] = None
    padding: Union[str, None] = None
