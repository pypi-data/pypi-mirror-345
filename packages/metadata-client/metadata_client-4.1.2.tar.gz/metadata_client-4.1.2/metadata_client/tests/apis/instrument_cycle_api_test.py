"""InstrumentCycleApiTest class"""

import unittest
from datetime import datetime, timedelta, timezone

from metadata_client import MetadataClient
from .api_base import ApiBase
from ..common.config_test import *
from ..common.generators import Generators
from ..common.secrets import *
from ..common.util_datetime import UtilDatetime as util_dt


class InstrumentCycleApiTest(ApiBase, unittest.TestCase):
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
    begin_at = datetime(__now.year, __now.month, __now.day,
                        __now.hour, __now.minute, __now.second,
                        __now.microsecond, tzinfo=__utc)
    __half_year = __now + timedelta(182)
    end_at = datetime(__half_year.year, __half_year.month, __half_year.day,
                      __half_year.hour, __half_year.minute,
                      __half_year.second, __half_year.microsecond,
                      tzinfo=__utc)
    __call_year = __now - timedelta(365)
    start_call_at = datetime(__call_year.year, __call_year.month,
                             __call_year.day,
                             __call_year.hour, __call_year.minute,
                             __call_year.second, __call_year.microsecond,
                             tzinfo=__utc)

    __call_half_year = __call_year + timedelta(182)
    close_call_at = datetime(__call_half_year.year, __call_half_year.month,
                             __call_half_year.day,
                             __call_half_year.hour, __call_half_year.minute,
                             __call_half_year.second,
                             __call_half_year.microsecond,
                             tzinfo=__utc)

    def test_create_instrument_cycle_api(self):
        __unique_id = Generators.generate_unique_id(min_value=202401,
                                                    max_value=202409)

        instrument_cycle = {
            'instrument_cycle': {
                'identifier': __unique_id,
                'instrument_id': '504',
                'instrument_identifier': 'JTM',
                'begin_at': util_dt.datetime_to_local_tz_str(self.begin_at),
                'end_at': util_dt.datetime_to_local_tz_str(self.end_at),
                'start_call_at': util_dt.datetime_to_local_tz_str(
                    self.start_call_at),
                'close_call_at': util_dt.datetime_to_local_tz_str(
                    self.close_call_at),
                'url': 'https://in.xfel.eu/upex/instrument_cycle/{0}'.format(
                    __unique_id),
                'flg_proposal_system': 'upex',
                'flg_available': 'true',
                'description': 'desc 01'
            }
        }

        expect = instrument_cycle['instrument_cycle']

        #
        # Create new entry (should succeed)
        #
        received = self.__create_entry_api(instrument_cycle, expect)

        instrument_cycle_id = received['id']

        #
        # Create duplicated entry (should throw an error)
        #
        self.__create_error_entry_uk_api(instrument_cycle)

        #
        # Get entry by ID
        #
        self.__get_entry_by_id_api(instrument_cycle_id, expect)

        #
        # Put entry information (update some fields should succeed)
        #
        self.__update_entry_api(instrument_cycle_id, expect)

        #
        # Delete entry (should succeed)
        # (test purposes only to keep the DB clean)
        #
        self.__delete_entry_by_id_api(instrument_cycle_id)

    #
    # fields_validation
    #
    def fields_validation(self, receive, expect):
        self.assert_eq_hfield(receive, expect, 'identifier', NUMBER)
        self.assert_eq_hfield(receive, expect, 'url', STRING)
        self.assert_eq_hfield(receive, expect, 'instrument_id', NUMBER)
        self.assert_eq_hfield(receive, expect,
                              'instrument_identifier', STRING)
        self.assert_eq_hfield(receive, expect, 'begin_at', DATETIME)
        self.assert_eq_hfield(receive, expect, 'end_at', DATETIME)
        self.assert_eq_hfield(receive, expect, 'start_call_at', DATETIME)
        self.assert_eq_hfield(receive, expect, 'close_call_at', DATETIME)
        self.assert_eq_hfield(receive, expect,
                              'flg_proposal_system', STRING)
        self.assert_eq_hfield(receive, expect, 'flg_available', BOOLEAN)
        self.assert_eq_hfield(receive, expect, 'description', STRING)

    #
    # Internal private APIs methods
    #
    def __create_entry_api(self, entry_info, expect):
        response = self.client_api.create_instrument_cycle_api(entry_info)
        receive = self.get_and_validate_create_entry(response)
        self.fields_validation(receive, expect)
        return receive

    def __create_error_entry_uk_api(self, entry_info):
        response = self.client_api.create_instrument_cycle_api(entry_info)
        resp_content = self.load_response_content(response)

        receive = resp_content
        expect = {'info': {'identifier': ['has already been taken'],
                           'url': ['has already been taken'],
                           'instrument_id': ['has already been taken']}}

        self.assertEqual(receive, expect, "Expected result not received")
        self.assert_eq_status_code(response.status_code, UNPROCESSABLE_ENTITY)

        # 'has already been taken'
        receive_msg = receive['info']['identifier'][0]
        expect_msg = expect['info']['identifier'][0]
        self.assert_eq_str(receive_msg, expect_msg)

    def __update_entry_api(self, entry_id, expect):
        __unique_id = Generators.generate_unique_id(min_value=201701,
                                                    max_value=201709)

        __begin_at = self.begin_at + timedelta(1)
        __end_at = self.end_at + timedelta(1)
        __start_call_at = self.start_call_at + timedelta(1)
        __close_call_at = self.close_call_at + timedelta(1)

        instrument_cycle_upd = {
            'instrument_cycle': {
                'identifier': __unique_id,
                'url': 'https://in.xfel.eu/upex/instrument_cycle/{0}'.format(
                    __unique_id),
                'instrument_id': '111',
                'instrument_identifier': 'ITLAB',
                'begin_at': util_dt.datetime_to_local_tz_str(__begin_at),
                'end_at': util_dt.datetime_to_local_tz_str(__end_at),
                'start_call_at': util_dt.datetime_to_local_tz_str(
                    __start_call_at),
                'close_call_at': util_dt.datetime_to_local_tz_str(
                    __close_call_at),
                'flg_proposal_system': 'upex',
                'flg_available': 'false',
                'description': 'desc 01 updated!!!'
            }
        }

        response = self.client_api.update_instrument_cycle_api(
            entry_id, instrument_cycle_upd)

        resp_content = self.load_response_content(response)

        receive = resp_content
        expect_upd = instrument_cycle_upd['instrument_cycle']

        print(expect)
        print(expect_upd)

        self.fields_validation(receive, expect_upd)
        self.assert_eq_status_code(response.status_code, OK)

        field = 'identifier'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)
        field = 'url'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)
        field = 'instrument_id'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)
        field = 'instrument_identifier'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)
        field = 'begin_at'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)
        field = 'end_at'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)
        field = 'start_call_at'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)
        field = 'close_call_at'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)
        field = 'flg_proposal_system'
        self.assert_eq_str(expect[field], expect_upd[field])
        field = 'flg_available'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)
        field = 'description'
        self.assert_not_eq_str(expect[field], expect_upd[field], field)

    def __get_entry_by_id_api(self, entry_id, expect):
        response = self.client_api.get_instrument_cycle_by_id_api(entry_id)
        receive = self.get_and_validate_entry_by_id(response)
        self.fields_validation(receive, expect)

    def __delete_entry_by_id_api(self, entry_id):
        response = self.client_api.delete_instrument_cycle_api(entry_id)
        self.get_and_validate_delete_entry_by_id(response)


if __name__ == '__main__':
    unittest.main()
