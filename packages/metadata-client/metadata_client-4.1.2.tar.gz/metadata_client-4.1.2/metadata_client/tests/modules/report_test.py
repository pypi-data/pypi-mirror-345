"""ReportTest class"""

import copy
import unittest

from metadata_client.metadata_client import MetadataClient
from .module_base import ModuleBase
from ..common.config_test import *
from ..common.secrets import *
from ...modules.report import Report

MODULE_NAME = REPORT


class ReportTest(ModuleBase, unittest.TestCase):
    def setUp(self):
        self.mdc_client = MetadataClient(
            client_id=CLIENT_OAUTH2_INFO['CLIENT_ID'],
            client_secret=CLIENT_OAUTH2_INFO['CLIENT_SECRET'],
            token_url=CLIENT_OAUTH2_INFO['TOKEN_URL'],
            refresh_url=CLIENT_OAUTH2_INFO['REFRESH_URL'],
            auth_url=CLIENT_OAUTH2_INFO['AUTH_URL'],
            scope=CLIENT_OAUTH2_INFO['SCOPE'],
            user_email=CLIENT_OAUTH2_INFO['EMAIL'],
            base_api_url=BASE_API_URL
        )

        self.report_01 = {
            'name': 'FXE_XAD_JF1M_correct_900203_r9037_230621_114538_v20.pdf',
            'cal_report_path':
                '/gpfs/exfel/exp/CALLAB/202130/p700203/usr/Reports/r9037/',
            'cal_report_at': '2023-05-25T08:30:00.000+02:00',
            'run_id': '-1',
            'description': 'Special report for existing run!'
        }

        self.report_01_upd = {
            'name': 'FXE_XAD_JF1M_correct_900203_r9037_230621_114538_v21.pdf',
            'cal_report_path':
                '/gpfs/exfel/exp/CALLAB/202130/p700203/usr/Reports/r0001/',
            'cal_report_at': '2023-06-25T08:30:00.000+02:00',
            'run_id': '-1',
            'description': 'Special report for existing run - UPDATED!!!'
        }

    def test_create_report(self):
        report_01 = Report(
            metadata_client=self.mdc_client,
            name=self.report_01['name'],
            cal_report_path=self.report_01['cal_report_path'],
            cal_report_at=self.report_01['cal_report_at'],
            run_id=self.report_01['run_id'],
            description=self.report_01['description']
        )

        #
        # Create new entry (should succeed)
        #
        result1 = report_01.create()
        self.assert_create_success(MODULE_NAME, result1, self.report_01)

        report_id = result1['data']['id']
        run_id = result1['data']['run_id']

        #
        # Create duplicated entry (should throw an error)
        #
        report_01_dup = copy.copy(report_01)
        result2 = report_01_dup.create()
        expect_app_info = {'name': ['has already been taken'],
                           'cal_report_path': ['has already been taken'],
                           'run_id': ['has already been taken']}
        self.assert_create_error(MODULE_NAME, result2, expect_app_info)

        #
        # Get all by run_id
        #
        result31 = Report.get_all_by_run_id(self.mdc_client, run_id)
        self.fields_validation(result31['data'][0], self.report_01)

        #
        # Get entry by ID
        #
        result4 = Report.get_by_id(self.mdc_client, report_id)
        self.assert_find_success(MODULE_NAME, result4, self.report_01)

        #
        # Get entry with non-existent ID (should throw an error)
        #
        result5 = Report.get_by_id(self.mdc_client, -666)
        self.assert_find_error(MODULE_NAME, result5, RESOURCE_NOT_FOUND)

        #
        # Put entry information (update some fields should succeed)
        #
        report_01.name = self.report_01_upd['name']
        report_01.cal_report_path = self.report_01_upd['cal_report_path']
        report_01.cal_report_at = self.report_01_upd['cal_report_at']
        report_01.run_id = self.report_01_upd['run_id']
        report_01.description = self.report_01_upd['description']
        result6 = report_01.update()
        self.assert_update_success(MODULE_NAME, result6, self.report_01_upd)

        #
        # Put entry information (update some fields should throw an error)
        #
        tmp_name = '______THIS__NAME__HAS_NO_PDF_AT_THE_END______'
        tmp_name_incorrect = tmp_name * 6
        report_01.name = tmp_name_incorrect
        report_01.description = self.report_01_upd['description']
        result7 = report_01.update()
        expect_app_info = {
            'name': ['is too long (maximum is 128 characters)',
                     'cannot contain spaces and must end with .pdf']}

        self.assert_update_error(MODULE_NAME, result7, expect_app_info)

        #
        # Delete entry (should succeed)
        # (test purposes only to keep the DB clean)
        #
        result8 = report_01.delete()
        self.assert_delete_success(MODULE_NAME, result8)

        #
        # Delete entry (should throw an error)
        # (test purposes only to keep the DB clean)
        #
        result9 = report_01.delete()
        self.assert_delete_error(MODULE_NAME, result9, RESOURCE_NOT_FOUND)

    #
    # fields_validation
    #
    def fields_validation(self, receive, expect):
        self.assert_eq_hfield(receive, expect, 'name', STRING)
        self.assert_eq_hfield(receive, expect, 'cal_report_path', STRING)
        self.assert_eq_hfield(receive, expect, 'cal_report_at', DATETIME)
        self.assert_eq_hfield(receive, expect, 'run_id', NUMBER)
        self.assert_eq_hfield(receive, expect, 'description', STRING)


if __name__ == '__main__':
    unittest.main()
