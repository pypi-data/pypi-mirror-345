# from humps import camelize
from pydantic import BaseModel, ConfigDict


class ParamsBaseModel(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )
    # class Config:
    #     arbitrary_types_allowed = True
    # #     alias_generator = camelize
    # #     populate_by_name = True
