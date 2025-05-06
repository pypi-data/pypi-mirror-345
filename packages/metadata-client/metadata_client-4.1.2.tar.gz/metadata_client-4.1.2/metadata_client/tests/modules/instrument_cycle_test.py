"""InstrumentCycleTest class"""

import unittest
from datetime import datetime, timedelta, timezone

from metadata_client import MetadataClient
from .module_base import ModuleBase
from ..common.config_test import *
from ..common.generators import Generators
from ..common.secrets import *
from ...modules.instrument_cycle import InstrumentCycle

from ..common.util_datetime import UtilDatetime as util_dt

MODULE_NAME = INSTRUMENT_CYCLE


class InstrumentCycleTest(ModuleBase, unittest.TestCase):
    def setUp(self):
        self.mdc_client = MetadataClient(
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
        self.begin_at = datetime(__now.year, __now.month, __now.day,
                                 __now.hour, __now.minute, __now.second,
                                 __now.microsecond, tzinfo=__utc)
        __half_year = __now + timedelta(182)
        self.end_at = datetime(__half_year.year, __half_year.month,
                               __half_year.day,
                               __half_year.hour, __half_year.minute,
                               __half_year.second, __half_year.microsecond,
                               tzinfo=__utc)
        __call_year = __now - timedelta(365)
        self.start_call_at = datetime(__call_year.year, __call_year.month,
                                      __call_year.day,
                                      __call_year.hour, __call_year.minute,
                                      __call_year.second,
                                      __call_year.microsecond,
                                      tzinfo=__utc)

        __call_half_year = __call_year + timedelta(182)
        self.close_call_at = datetime(__call_half_year.year,
                                      __call_half_year.month,
                                      __call_half_year.day,
                                      __call_half_year.hour,
                                      __call_half_year.minute,
                                      __call_half_year.second,
                                      __call_half_year.microsecond,
                                      tzinfo=__utc)

        __unique_id = Generators.generate_unique_id(min_value=202401,
                                                    max_value=202409)

        self.instrument_cycle_01 = {
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

        __unique_id_upd = Generators.generate_unique_id(min_value=201701,
                                                        max_value=201709)

        __begin_at_upd = self.begin_at + timedelta(1)
        __end_at_upd = self.end_at + timedelta(1)
        __start_call_at_upd = self.start_call_at + timedelta(1)
        __close_call_at_upd = self.close_call_at + timedelta(1)

        self.inst_cycle_01_upd = {
            'identifier': __unique_id_upd,
            'url': 'https://in.xfel.eu/upex/instrument_cycle/{0}'.format(
                __unique_id),
            'instrument_id': '111',
            'instrument_identifier': 'ITLAB',
            'begin_at': util_dt.datetime_to_local_tz_str(__begin_at_upd),
            'end_at': util_dt.datetime_to_local_tz_str(__end_at_upd),
            'start_call_at': util_dt.datetime_to_local_tz_str(
                __start_call_at_upd),
            'close_call_at': util_dt.datetime_to_local_tz_str(
                __close_call_at_upd),
            'flg_proposal_system': 'upex',
            'flg_available': 'false',
            'description': 'desc 01 updated!!!'
        }

    def test_create_instrument_cycle(self):
        inst_cycle_01 = InstrumentCycle(
            metadata_client=self.mdc_client,
            identifier=self.instrument_cycle_01['identifier'],
            instrument_id=self.instrument_cycle_01['instrument_id'],
            instrument_identifier=self.instrument_cycle_01[
                'instrument_identifier'],
            begin_at=self.instrument_cycle_01['begin_at'],
            end_at=self.instrument_cycle_01['end_at'],
            start_call_at=self.instrument_cycle_01['start_call_at'],
            close_call_at=self.instrument_cycle_01['close_call_at'],
            url=self.instrument_cycle_01['url'],
            flg_available=self.instrument_cycle_01['flg_available'],
            flg_proposal_system=self.instrument_cycle_01[
                'flg_proposal_system'],
            description=self.instrument_cycle_01['description']
        )

        #
        # Create new entry (should succeed)
        #
        result1 = inst_cycle_01.create()
        self.assert_create_success(MODULE_NAME,
                                   result1, self.instrument_cycle_01)

        instrument_cycle_id = result1['data']['id']
        # sample_name = result1['data']['name']
        # sample_proposal_id = result1['data']['proposal_id']

        #
        # Create duplicated entry (should throw an error)
        #
        instrument_cycle_01_dup = inst_cycle_01
        result2 = instrument_cycle_01_dup.create()
        expect_app_info = {'identifier': ['has already been taken']}
        self.assert_create_error(MODULE_NAME, result2, expect_app_info)

        #
        # Get entry by ID
        #
        result4 = InstrumentCycle.get_by_id(self.mdc_client,
                                            instrument_cycle_id)
        self.assert_find_success(MODULE_NAME,
                                 result4, self.instrument_cycle_01)

        #
        # Get entry with non-existent ID (should throw an error)
        #
        result5 = InstrumentCycle.get_by_id(self.mdc_client, -666)
        self.assert_find_error(MODULE_NAME, result5, RESOURCE_NOT_FOUND)

        #
        # Put entry information (update some fields should succeed)
        #
        inst_cycle_01.identifier = self.inst_cycle_01_upd['identifier']
        inst_cycle_01.url = self.inst_cycle_01_upd['url']
        inst_cycle_01.instrument_identifier = self.inst_cycle_01_upd[
            'instrument_identifier']
        inst_cycle_01.instrument_id = self.inst_cycle_01_upd['instrument_id']
        inst_cycle_01.flg_proposal_system = self.inst_cycle_01_upd[
            'flg_proposal_system']

        inst_cycle_01.begin_at = self.inst_cycle_01_upd['begin_at']
        inst_cycle_01.end_at = self.inst_cycle_01_upd['end_at']
        inst_cycle_01.start_call_at = self.inst_cycle_01_upd['start_call_at']
        inst_cycle_01.close_call_at = self.inst_cycle_01_upd['close_call_at']
        inst_cycle_01.flg_available = self.inst_cycle_01_upd['flg_available']
        inst_cycle_01.description = self.inst_cycle_01_upd['description']

        result6 = inst_cycle_01.update()
        self.assert_update_success(MODULE_NAME,
                                   result6, self.inst_cycle_01_upd)

        #
        # Delete entry (should succeed)
        # (test purposes only to keep the DB clean)
        #
        result8 = inst_cycle_01.delete()
        self.assert_delete_success(MODULE_NAME, result8)

        #
        # Delete entry (should throw an error)
        # (test purposes only to keep the DB clean)
        #
        result9 = inst_cycle_01.delete()
        self.assert_delete_error(MODULE_NAME, result9, RESOURCE_NOT_FOUND)

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


if __name__ == '__main__':
    unittest.main()
