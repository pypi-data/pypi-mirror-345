"""TechniqueApi module class"""

import json

from ..common.base import Base
from ..common.config import *


class TechniqueApi(Base):
    def create_technique_api(self, technique):
        api_url = self.__get_api_url()
        return self.api_post(api_url, data=json.dumps(technique))

    def delete_technique_api(self, technique_id):
        api_url = self.__get_api_url(technique_id)
        return self.api_delete(api_url)

    def update_technique_api(self, technique_id, technique):
        api_url = self.__get_api_url(technique_id)
        return self.api_put(api_url, data=json.dumps(technique))

    def get_technique_by_id_api(self, technique_id):
        api_url = self.__get_api_url(technique_id)
        return self.api_get(api_url, params={})

    def get_technique_by_identifier_api(self, identifier,
                                        page=DEF_PAGE,
                                        page_size=DEF_PAGE_SIZE):
        api_url = self.__get_api_url()
        return self.api_get(api_url, params={'identifier': identifier,
                                             'page': page,
                                             'page_size': page_size})

    def get_all_techniques_by_name_api(self, name,
                                       page=DEF_PAGE,
                                       page_size=DEF_PAGE_SIZE):
        api_url = self.__get_api_url()
        return self.api_get(api_url, params={'name': name,
                                             'page': page,
                                             'page_size': page_size})

    def get_all_techniques_by_identifier_api(self, identifier,
                                             page=DEF_PAGE,
                                             page_size=DEF_PAGE_SIZE):
        api_url = self.__get_api_url()
        return self.api_get(api_url, params={'identifier': identifier,
                                             'page': page,
                                             'page_size': page_size})

    #
    # Private Methods
    #
    def __get_api_url(self, api_specifics=''):
        model_name = 'techniques/'
        return self.get_api_url(model_name, api_specifics)
