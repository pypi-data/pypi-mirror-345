"""Technique module class"""

import inspect

from ..common.base import Base
from ..common.config import *

MODULE_NAME = TECHNIQUE


class Technique:
    def __init__(self, metadata_client,
                 identifier, name, url,
                 flg_xfel_available,
                 flg_available, description=''):
        self.metadata_client = metadata_client
        self.id = None
        self.identifier = identifier
        self.name = name
        self.url = url
        self.flg_xfel_available = flg_xfel_available
        self.flg_available = flg_available
        self.description = description

    def create(self):
        mdc_client = self.metadata_client
        response = mdc_client.create_technique_api(self.__get_resource())

        Base.cal_debug(MODULE_NAME, CREATE, response)
        res = Base.format_response(response, CREATE, CREATED, MODULE_NAME)

        if res['success']:
            self.id = res['data']['id']

        return res

    def delete(self):
        mdc_client = self.metadata_client
        response = mdc_client.delete_technique_api(self.id)
        Base.cal_debug(MODULE_NAME, DELETE, response)

        return Base.format_response(response, DELETE, NO_CONTENT, MODULE_NAME)

    def update(self):
        mdc_client = self.metadata_client
        response = mdc_client.update_technique_api(self.id,
                                                   self.__get_resource())

        Base.cal_debug(MODULE_NAME, UPDATE, response)
        return Base.format_response(response, UPDATE, OK, MODULE_NAME)

    @staticmethod
    def set_by_name(mdc_client, technique_h):
        resp = Technique.get_by_name(mdc_client,
                                     technique_h['name'])

        if resp['success'] and resp['data'] != {}:
            return resp

        new_technique = Technique(
            metadata_client=mdc_client,
            identifier=technique_h['identifier'],
            name=technique_h['name'],
            url=technique_h['url'],
            flg_xfel_available=technique_h['flg_xfel_available'],
            flg_available=technique_h['flg_available'],
            description=technique_h['description'])

        resp = new_technique.create()

        return resp

    @staticmethod
    def delete_by_id(mdc_client, technique_id):
        resp = mdc_client.delete_technique_api(technique_id)
        Base.cal_debug(MODULE_NAME, DELETE, resp)

        return Base.format_response(resp, DELETE, NO_CONTENT, MODULE_NAME)

    @staticmethod
    def get_by_id(mdc_client, technique_id):
        response = mdc_client.get_technique_by_id_api(technique_id)

        curr_method_name = inspect.currentframe().f_code.co_name
        Base.cal_debug(MODULE_NAME, curr_method_name, response)
        return Base.format_response(response, GET, OK, MODULE_NAME)

    @staticmethod
    def get_by_name(mdc_client, name,
                    page=DEF_PAGE, page_size=DEF_PAGE_SIZE):
        res = Technique.get_all_by_name(
            mdc_client, name, page, page_size)

        if res['success']:
            res = Base.unique_key_format_result(res=res,
                                                module_name=MODULE_NAME)

        return res

    @staticmethod
    def get_all_by_name(mdc_client, name,
                        page=DEF_PAGE,
                        page_size=DEF_PAGE_SIZE):
        response = mdc_client.get_all_techniques_by_name_api(
            name, page, page_size)

        curr_method_name = inspect.currentframe().f_code.co_name
        Base.cal_debug(MODULE_NAME, curr_method_name, response)
        return Base.format_response(response, GET, OK, MODULE_NAME)

    @staticmethod
    def get_by_identifier(mdc_client, identifier,
                          page=DEF_PAGE, page_size=DEF_PAGE_SIZE):
        response = mdc_client.get_technique_by_identifier_api(
            identifier, page, page_size)

        curr_method_name = inspect.currentframe().f_code.co_name
        Base.cal_debug(MODULE_NAME, curr_method_name, response)
        res = Base.format_response(response, GET, OK, MODULE_NAME)

        if res['success']:
            res = Base.unique_key_format_result(res=res,
                                                module_name=MODULE_NAME)

        return res

    def __get_resource(self):
        technique = {
            MODULE_NAME: {
                'identifier': self.identifier,
                'name': self.name,
                'url': self.url,
                'flg_xfel_available': self.flg_xfel_available,
                'flg_available': self.flg_available,
                'description': self.description
            }
        }

        return technique
