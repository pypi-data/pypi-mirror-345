"""Report module class"""
import inspect

from ..common.base import Base
from ..common.config import *

MODULE_NAME = REPORT


class Report:
    def __init__(self, metadata_client,
                 name, cal_report_path, cal_report_at,
                 run_id, description=''):
        self.metadata_client = metadata_client
        self.id = None
        self.name = name
        self.cal_report_path = cal_report_path
        self.cal_report_at = cal_report_at
        self.run_id = run_id
        self.description = description

    def create(self):
        mdc_client = self.metadata_client
        response = mdc_client.create_report_api(self.__get_resource())

        Base.cal_debug(MODULE_NAME, CREATE, response)
        res = Base.format_response(response, CREATE, CREATED, MODULE_NAME)

        if res['success']:
            self.id = res['data']['id']

        return res

    def delete(self):
        mdc_client = self.metadata_client
        response = mdc_client.delete_report_api(self.id)
        Base.cal_debug(MODULE_NAME, DELETE, response)

        return Base.format_response(response, DELETE, NO_CONTENT, MODULE_NAME)

    def update(self):
        mdc_client = self.metadata_client
        response = mdc_client.update_report_api(self.id,
                                                self.__get_resource())

        Base.cal_debug(MODULE_NAME, UPDATE, response)
        return Base.format_response(response, UPDATE, OK, MODULE_NAME)

    @staticmethod
    def get_by_id(mdc_client, report_id):
        response = mdc_client.get_report_by_id_api(report_id)

        curr_method_name = inspect.currentframe().f_code.co_name
        Base.cal_debug(MODULE_NAME, curr_method_name, response)
        return Base.format_response(response, GET, OK, MODULE_NAME)

    @staticmethod
    def get_all_by_run_id(mdc_client, run_id, page=DEF_PAGE,
                          page_size=DEF_PAGE_SIZE):
        resp = mdc_client.get_all_reports_by_run_id_api(
            run_id, page, page_size)

        curr_method_name = inspect.currentframe().f_code.co_name
        Base.cal_debug(MODULE_NAME, curr_method_name, resp)
        return Base.format_response(resp, GET, OK, MODULE_NAME)

    def __get_resource(self):
        report = {
            MODULE_NAME: {
                'name': self.name,
                'cal_report_path': self.cal_report_path,
                'cal_report_at': self.cal_report_at,
                'run_id': self.run_id,
                'description': self.description
            }
        }

        return report
