"""InstrumentCycle module class"""

import inspect

from ..common.base import Base
from ..common.config import *

MODULE_NAME = INSTRUMENT_CYCLE


class InstrumentCycle:
    def __init__(self, metadata_client,
                 identifier, instrument_id, instrument_identifier,
                 begin_at, end_at, start_call_at, close_call_at,
                 url, flg_available, flg_proposal_system, description=''):
        self.metadata_client = metadata_client
        self.id = None
        self.identifier = identifier
        self.instrument_id = instrument_id
        self.instrument_identifier = instrument_identifier
        self.begin_at = begin_at
        self.end_at = end_at
        self.start_call_at = start_call_at
        self.close_call_at = close_call_at
        self.url = url
        self.flg_available = flg_available
        self.flg_proposal_system = flg_proposal_system
        self.description = description

    def create(self):
        mdc_client = self.metadata_client
        resp = mdc_client.create_instrument_cycle_api(self.__get_resource())

        Base.cal_debug(MODULE_NAME, CREATE, resp)
        res = Base.format_response(resp, CREATE, CREATED, MODULE_NAME)

        if res['success']:
            self.id = res['data']['id']

        return res

    def delete(self):
        mdc_client = self.metadata_client
        response = mdc_client.delete_instrument_cycle_api(self.id)
        Base.cal_debug(MODULE_NAME, DELETE, response)

        return Base.format_response(response, DELETE, NO_CONTENT, MODULE_NAME)

    def update(self):
        mdc_client = self.metadata_client
        resp = mdc_client.update_instrument_cycle_api(self.id,
                                                      self.__get_resource())

        Base.cal_debug(MODULE_NAME, UPDATE, resp)
        return Base.format_response(resp, UPDATE, OK, MODULE_NAME)

    @staticmethod
    def delete_by_id(mdc_client, sample_id):
        resp = mdc_client.delete_instrument_cycle_api(sample_id)
        Base.cal_debug(MODULE_NAME, DELETE, resp)

        return Base.format_response(resp, DELETE, NO_CONTENT, MODULE_NAME)

    @staticmethod
    def get_by_id(mdc_client, sample_id):
        response = mdc_client.get_instrument_cycle_by_id_api(sample_id)

        curr_method_name = inspect.currentframe().f_code.co_name
        Base.cal_debug(MODULE_NAME, curr_method_name, response)
        return Base.format_response(response, GET, OK, MODULE_NAME)

    def __get_resource(self):
        instrument_cycle = {
            MODULE_NAME: {
                'identifier': self.identifier,
                'instrument_id': self.instrument_id,
                'instrument_identifier': self.instrument_identifier,
                'begin_at': self.begin_at,
                'end_at': self.end_at,
                'start_call_at': self.start_call_at,
                'close_call_at': self.close_call_at,
                'url': self.url,
                'flg_available': self.flg_available,
                'flg_proposal_system': self.flg_proposal_system,
                'description': self.description
            }
        }

        return instrument_cycle
