"""InstrumentCycleApi module class"""

import json

from ..common.base import Base
from ..common.config import *


class InstrumentCycleApi(Base):
    def create_instrument_cycle_api(self, instrument_cycle):
        api_url = self.__get_api_url()
        return self.api_post(api_url, data=json.dumps(instrument_cycle))

    def delete_instrument_cycle_api(self, instrument_cycle_id):
        api_url = self.__get_api_url(instrument_cycle_id)
        return self.api_delete(api_url)

    def update_instrument_cycle_api(self,
                                    instrument_cycle_id, instrument_cycle):
        api_url = self.__get_api_url(instrument_cycle_id)
        return self.api_put(api_url, data=json.dumps(instrument_cycle))

    def get_instrument_cycle_by_id_api(self, instrument_cycle_id):
        api_url = self.__get_api_url(instrument_cycle_id)
        return self.api_get(api_url, params={})

    #
    # Private Methods
    #
    def __get_api_url(self, api_specifics=''):
        model_name = 'instrument_cycles/'
        return self.get_api_url(model_name, api_specifics)
