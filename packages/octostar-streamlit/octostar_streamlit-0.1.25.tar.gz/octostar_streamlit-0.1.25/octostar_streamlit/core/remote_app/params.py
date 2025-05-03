from octostar_streamlit.core.params_base_model import ParamsBaseModel


class SubscribeToContextParams(ParamsBaseModel):
    id: str


class UbsubscribeFromContextParams(ParamsBaseModel):
    id: str
