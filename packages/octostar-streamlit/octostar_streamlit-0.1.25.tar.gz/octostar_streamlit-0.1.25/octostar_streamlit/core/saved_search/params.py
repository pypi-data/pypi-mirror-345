from typing import Union

from octostar_streamlit.core.entities import Entity
from octostar_streamlit.core.params_base_model import ParamsBaseModel

class SavedSearchIdn(ParamsBaseModel):
    entity: Union[str, Entity]
    def model_dump(self, **kwargs):
        base_dict = super().model_dump(**kwargs)
        if isinstance(self.entity, Entity):
            base_dict['entity'] = self.entity.to_dict()
        return base_dict
