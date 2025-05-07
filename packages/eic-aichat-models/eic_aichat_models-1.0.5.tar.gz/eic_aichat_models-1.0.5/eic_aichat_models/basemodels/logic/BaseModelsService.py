from typing import Optional

from pip_services4_components.config import ConfigParams, IConfigurable
from pip_services4_components.context import IContext
from pip_services4_components.refer import IReferences, IReferenceable, Descriptor
from pip_services4_data.keys import IdGenerator
from pip_services4_data.query import DataPage, PagingParams, FilterParams

from ..data import BaseModel
from ..persistence import IBaseModelsPersistence

from .IBaseModelsService import IBaseModelsService


class BaseModelsService(IBaseModelsService, IConfigurable, IReferenceable):
    __persistence: IBaseModelsPersistence = None

    def configure(self, config: ConfigParams):
        pass

    def set_references(self, references: IReferences):
        self.__persistence = references.get_one_required(Descriptor('aichatmodels-basemodels', 'persistence', '*', '*', '1.0'))
        
        # temporary automatic model creation
        model = self.__persistence.get_one_by_id(None, '1')
        if model == None:
            model == BaseModel('1', 'OpenAI', 'openai', 'https://api.openai.com/v1', ['gpt-3.5-turbo', 'gpt-4-turbo', 'gpt-4o'])
            self.__persistence.create(None, model)

    def get_models(self, context: Optional[IContext], filter_params: FilterParams,
                   paging: PagingParams) -> DataPage:
        return self.__persistence.get_page_by_filter(context, filter_params, paging)

    def get_model_by_id(self, context: Optional[IContext], model_id: str) -> BaseModel:
        return self.__persistence.get_one_by_id(context, model_id)

    def get_model_by_api(self, context: Optional[IContext], api: str) -> BaseModel:
        return self.__persistence.get_one_by_api(context, api)
    
    def get_model_by_name(self, context: Optional[IContext], name: str) -> BaseModel:
        return self.__persistence.get_one_by_name(context, name)

    def create_model(self, context: Optional[IContext], model: BaseModel) -> BaseModel:
        model.id = model.id or IdGenerator.next_long()

        return self.__persistence.create(context, model)

    def update_model(self, context: Optional[IContext], model: BaseModel) -> BaseModel:

        return self.__persistence.update(context, model)

    def delete_model_by_id(self, context: Optional[IContext], model_id: str) -> BaseModel:
        return self.__persistence.delete_by_id(context, model_id)