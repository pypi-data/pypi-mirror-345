"""UnitApiTest class"""

import unittest
from datetime import datetime, timedelta, timezone

from metadata_client import MetadataClient
from .api_base import ApiBase
from ..common.config_test import *
from ..common.generators import Generators
from ..common.secrets import *
from ..common.util_datetime import UtilDatetime as util_dt


class UnitApiTest(ApiBase, unittest.TestCase):
    client_api = MetadataClient(
        client_id=CLIENT_OAUTH2_INFO['CLIENT_ID'],
        client_secret=CLIENT_OAUTH2_INFO['CLIENT_SECRET'],
        token_url=CLIENT_OAUTH2_INFO['TOKEN_URL'],
        refresh_url=CLIENT_OAUTH2_INFO['REFRESH_URL'],
        auth_url=CLIENT_OAUTH2_INFO['AUTH_URL'],
        scope=CLIENT_OAUTH2_INFO['SCOPE'],
        user_email=CLIENT_OAUTH2_INFO['EMAIL'],
        base_api_url=BASE_API_URL)

    __utc = timezone(timedelta())

    __now = datetime.now()
    __yesterday = __now - timedelta(1)

    date_01 = datetime(__yesterday.year, __yesterday.month, __yesterday.day,
                       __yesterday.hour, __yesterday.minute,
                       __yesterday.second, __yesterday.microsecond,
                       tzinfo=__utc)

    date_02 = datetime(__now.year, __now.month, __now.day,
                       __now.hour, __now.minute, __now.second,
                       __now.microsecond, tzinfo=__utc)

    def test_create_unit_api(self):
        __unique_name = Generators.generate_unique_name('UnitApi')
        __unique_identifier = Generators.generate_unique_identifier()
        unit = {
            'unit': {
                'name': __unique_name,
                'identifier': __unique_identifier,
                'symbol': "Sy",
                'origin': "test",
                'flg_available': 'true',
                'description': 'desc 01',
                'created_at': util_dt.datetime_to_local_tz_str(self.date_01),
                'updated_at': util_dt.datetime_to_local_tz_str(self.date_01),
            }
        }

        expect = unit['unit']

        #
        # Create new entry (should succeed)
        #
        received = self.__create_entry_api(unit, expect)

        unit_id = received['id']
        unit_name = received['name']

        #
        # Create duplicated entry (should throw an error)
        #
        self.__create_error_entry_uk_api(unit)

        #
        # Get entry by name
        #
        self.__get_all_entries_api(unit_name, expect)

        #
        # Get entry by ID
        #
        self.__get_entry_by_id_api(unit_id, expect)

        #
        # Put entry information (update some fields should succeed)
        #
        self.__update_entry_api(unit_id, expect)

        #
        # Delete entry (should succeed)
        # (test purposes only to keep the DB clean)
        #
        self.__delete_entry_by_id_api(unit_id)

    #
    # fields_validation
    #
    def fields_validation(self, receive, expect):
        self.assert_eq_hfield(receive, expect, 'name', STRING)
        self.assert_eq_hfield(receive, expect, 'identifier', STRING)
        self.assert_eq_hfield(receive, expect, 'symbol', STRING)
        self.assert_eq_hfield(receive, expect, 'origin', STRING)
        self.assert_eq_hfield(receive, expect, 'flg_available', BOOLEAN)
        self.assert_eq_hfield(receive, expect, 'description', STRING)
        # self.assert_eq_hfield(receive, expect, 'created_at', DATETIME)
        # self.assert_eq_hfield(receive, expect, 'updated_at', DATETIME)

    #
    # Internal private APIs methods
    #
    def __create_entry_api(self, entry_info, expect):
        response = self.client_api.create_unit_api(entry_info)
        receive = self.get_and_validate_create_entry(response)
        self.fields_validation(receive, expect)
        return receive

    def __create_error_entry_uk_api(self, entry_info):
        response = self.client_api.create_unit_api(entry_info)
        resp_content = self.load_response_content(response)

        receive = resp_content
        expect = {'info': {'identifier': ['has already been taken'],
                           'name': ['has already been taken']}}

        self.assertEqual(receive, expect, "Expected result not received")
        self.assert_eq_status_code(response.status_code, UNPROCESSABLE_ENTITY)

        # 'has already been taken'
        receive_msg = receive['info']['name'][0]
        expect_msg = expect['info']['name'][0]
        self.assert_eq_str(receive_msg, expect_msg)

    def __update_entry_api(self, entry_id, expect):
        unique_name_upd = Generators.generate_unique_name('ExpUnitApiUpd')
        unique_id_upd = Generators.generate_unique_identifier(1)
        unit_upd = {
            'unit': {
                'name': unique_name_upd,
                'identifier': unique_id_upd,
                'symbol': "Sym",
                'origin': "testo",
                'flg_available': 'false',
                'description': 'desc 01 updated!!!',
                'created_at': util_dt.datetime_to_local_tz_str(self.date_02),
                'updated_at': util_dt.datetime_to_local_tz_str(self.date_02),
            }
        }

        response = self.client_api.update_unit_api(
            entry_id,
            unit_upd
        )

        resp_content = self.load_response_content(response)

        receive = resp_content
        expect_upd = unit_upd['unit']

        self.fields_validation(receive, expect_upd)
        self.assert_eq_status_code(response.status_code, OK)

        field = 'name'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)
        field = 'identifier'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)
        field = 'symbol'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)
        field = 'origin'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)
        field = 'flg_available'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)
        field = 'description'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)
        # field = 'created_at'
        # self.assert_not_eq_str(expect[field], expect_upd[field], field)
        # field = 'updated_at'
        # self.assert_not_eq_str(expect[field], expect_upd[field], field)

    def __get_all_entries_api(self, name, expect):
        response = self.client_api.get_all_units_api()
        receive = self.get_and_validate_all_entries_by_name(response)
        self.fields_validation(receive, expect)

    def __get_entry_by_id_api(self, entry_id, expect):
        response = self.client_api.get_unit_by_id_api(entry_id)
        receive = self.get_and_validate_entry_by_id(response)
        self.fields_validation(receive, expect)

    def __delete_entry_by_id_api(self, entry_id):
        response = self.client_api.delete_unit_api(entry_id)
        self.get_and_validate_delete_entry_by_id(response)


if __name__ == '__main__':
    unittest.main()
