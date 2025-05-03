from typing import Dict, List, Union

from octostar_streamlit.core.entities import EdgeSpec, Entity
from octostar_streamlit.core.params_base_model import ParamsBaseModel


class CreateLinkChartParams(ParamsBaseModel):
    name: str
    path: Union[str, None] = None
    # TODO: Test if Entity with additional_properties thing would be okay?
    nodes: Union[List[Entity], None] = None
    edges: Union[List[EdgeSpec], None] = None
    draft: Union[bool, None] = None
    os_workspace: Union[str, None] = None

    def model_dump(self, **kwargs):
        base_dict = super().model_dump(**kwargs)
        if self.nodes is not None:
            base_dict['nodes'] = [record.to_dict() for record in self.nodes]
        return base_dict
