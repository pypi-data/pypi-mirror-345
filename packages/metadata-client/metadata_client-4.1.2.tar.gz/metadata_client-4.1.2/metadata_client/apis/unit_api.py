"""UnitApi module class"""

import json

from ..common.base import Base
from ..common.config import *


class UnitApi(Base):
    def create_unit_api(self, unit):
        api_url = self.__get_api_url()
        return self.api_post(api_url, data=json.dumps(unit))

    def delete_unit_api(self, unit_id):
        api_url = self.__get_api_url(unit_id)
        return self.api_delete(api_url)

    def update_unit_api(self, unit_id, unit):
        api_url = self.__get_api_url(unit_id)
        return self.api_put(api_url, data=json.dumps(unit))

    def get_unit_by_id_api(self, unit_id):
        api_url = self.__get_api_url(unit_id)
        return self.api_get(api_url, params={})

    def get_all_units_api(self, page=DEF_PAGE,
                          page_size=DEF_PAGE_SIZE):
        api_url = self.__get_api_url()
        return self.api_get(api_url, params={'page': page,
                                             'page_size': page_size})

    #
    # Private Methods
    #
    def __get_api_url(self, api_specifics=''):
        model_name = 'units/'
        return self.get_api_url(model_name, api_specifics)
