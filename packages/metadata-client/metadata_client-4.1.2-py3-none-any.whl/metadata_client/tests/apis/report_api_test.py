"""ReportApiTest class"""

import unittest

from metadata_client import MetadataClient
from .api_base import ApiBase
from ..common.config_test import *
from ..common.secrets import *


class ReportApiTest(ApiBase, unittest.TestCase):
    client_api = MetadataClient(
        client_id=CLIENT_OAUTH2_INFO['CLIENT_ID'],
        client_secret=CLIENT_OAUTH2_INFO['CLIENT_SECRET'],
        token_url=CLIENT_OAUTH2_INFO['TOKEN_URL'],
        refresh_url=CLIENT_OAUTH2_INFO['REFRESH_URL'],
        auth_url=CLIENT_OAUTH2_INFO['AUTH_URL'],
        scope=CLIENT_OAUTH2_INFO['SCOPE'],
        user_email=CLIENT_OAUTH2_INFO['EMAIL'],
        base_api_url=BASE_API_URL)

    def test_create_report_api(self):
        report = {
            'report': {
                'name':
                    'FXE_XAD_JF1M_correct_900203_r9037_230621_114538_v2.pdf',
                'cal_report_path':
                    '/gpfs/exfel/exp/CALLAB/202130/p900203/usr/Reports/r9037/',
                'cal_report_at': '2023-05-25T08:30:00.000+02:00',
                'run_id': '-1',
                'description': 'Special report for existing run!'
            }
        }

        expect = report['report']

        #
        # Create new entry (should succeed)
        #
        received = self.__create_entry_api(report, expect)

        report_id = received['id']
        run_id = received['run_id']

        #
        # Get entry by ID
        #
        self.__get_entry_by_id_api(report_id, expect)

        #
        # Get all entries by RUN ID
        #
        self.__get_entry_by_run_id_api(run_id, expect)

        #
        # Put entry information (update some fields should succeed)
        #
        self.__update_entry_api(report_id, expect)

        #
        # Delete entry (should succeed)
        # (test purposes only to keep the DB clean)
        #
        self.__delete_entry_by_id_api(report_id)

    #
    # fields_validation
    #
    def fields_validation(self, receive, expect):
        self.assert_eq_hfield(receive, expect, 'name', STRING)
        self.assert_eq_hfield(receive, expect, 'cal_report_path', STRING)
        self.assert_eq_hfield(receive, expect, 'cal_report_at', DATETIME)
        self.assert_eq_hfield(receive, expect, 'run_id', NUMBER)
        self.assert_eq_hfield(receive, expect, 'description', STRING)

    #
    # Internal private APIs methods
    #
    def __create_entry_api(self, entry_info, expect):
        response = self.client_api.create_report_api(entry_info)
        receive = self.get_and_validate_create_entry(response)
        self.fields_validation(receive, expect)
        return receive

    def __get_entry_by_id_api(self, entry_id, expect):
        response = self.client_api.get_report_by_id_api(entry_id)
        receive = self.get_and_validate_entry_by_id(response)
        self.fields_validation(receive, expect)

    def __get_entry_by_run_id_api(self, run_id, expect):
        resp = self.client_api.get_all_reports_by_run_id_api(run_id)
        receive = self.get_and_validate_all_entries_by_name(resp)
        self.fields_validation(receive, expect)

    def __update_entry_api(self, entry_id, expect):
        report_upd = {
            'report': {
                'name':
                    'FXE_XAD_JF1M_correct_900203_r9037_230621_114538_v3.pdf',
                'cal_report_path':
                    '/gpfs/exfel/exp/CALLAB/202130/p900203/usr/Reports/r0001/',
                'cal_report_at': '2023-06-25T08:30:00.000+02:00',
                'run_id': '-1',
                'description': 'Special report for existing run - UPDATED!!!'
            }
        }

        response = self.client_api.update_report_api(entry_id,
                                                     report_upd)

        resp_content = self.load_response_content(response)

        receive = resp_content
        expect_upd = report_upd['report']

        self.fields_validation(receive, expect_upd)
        self.assert_eq_status_code(response.status_code, OK)

        field = 'name'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)
        field = 'cal_report_path'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)
        field = 'cal_report_at'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)
        field = 'run_id'
        self.assert_eq_str(expect[field], expect_upd[field])
        field = 'description'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)

    def __delete_entry_by_id_api(self, entry_id):
        response = self.client_api.delete_report_api(entry_id)
        self.get_and_validate_delete_entry_by_id(response)


if __name__ == '__main__':
    unittest.main()
