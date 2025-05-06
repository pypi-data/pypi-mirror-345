"""TechniqueTest class"""

import unittest

from metadata_client.metadata_client import MetadataClient
from .module_base import ModuleBase
from ..common.config_test import *
from ..common.generators import Generators
from ..common.secrets import *
from ...modules.technique import Technique

MODULE_NAME = TECHNIQUE


class TechniqueTest(ModuleBase, unittest.TestCase):
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

        __unique_ident1 = Generators.generate_unique_name_short('Tech01')
        self.tech_01 = {
            'name': __unique_ident1,
            'identifier': __unique_ident1,
            'url': '',
            'flg_xfel_available': 'false',
            'flg_available': 'true',
            'description': 'desc 01'
        }

        __unique_ident_upd = Generators.generate_unique_name_short('TechUpd1')
        self.tech_01_upd = {
            'name': __unique_ident_upd,
            'identifier': __unique_ident_upd,
            'url': '',
            'flg_xfel_available': 'false',
            'flg_available': 'true',
            'description': 'desc 01 updated!!!'
        }

    def test_create_experiment(self):
        tech_01 = Technique(
            metadata_client=self.mdc_client,
            identifier=self.tech_01['identifier'],
            name=self.tech_01['name'],
            url=self.tech_01['url'],
            flg_xfel_available=self.tech_01['flg_xfel_available'],
            flg_available=self.tech_01['flg_available'],
            description=self.tech_01['description'])

        #
        # Create new entry (should succeed)
        #
        result1 = tech_01.create()
        self.assert_create_success(MODULE_NAME, result1, self.tech_01)

        technique_id = result1['data']['id']
        technique_name = result1['data']['name']
        technique_identifier = result1['data']['identifier']

        #
        # Create duplicated entry (should throw an error)
        #
        tech_01_dup = tech_01
        result2 = tech_01_dup.create()
        expect_app_info = {'name': ['has already been taken'],
                           'identifier': ['has already been taken']}
        self.assert_create_error(MODULE_NAME, result2, expect_app_info)

        #
        # Get entry by name
        #
        result3 = Technique.get_by_name(self.mdc_client,
                                        technique_name)
        self.assert_find_success(MODULE_NAME, result3, self.tech_01)

        #
        # Get entry by proposal_id
        #
        result32 = Technique.get_by_identifier(self.mdc_client,
                                               technique_identifier)
        self.assert_find_success(MODULE_NAME, result32, self.tech_01)

        #
        # Get entry by ID
        #
        result4 = Technique.get_by_id(self.mdc_client, technique_id)
        self.assert_find_success(MODULE_NAME, result4, self.tech_01)

        #
        # Get entry with non-existent ID (should throw an error)
        #
        result5 = Technique.get_by_id(self.mdc_client, -666)
        self.assert_find_error(MODULE_NAME, result5, RESOURCE_NOT_FOUND)

        #
        # Put entry information (update some fields should succeed)
        #
        tech_01.name = self.tech_01_upd['name']
        tech_01.identifier = self.tech_01_upd['identifier']
        tech_01.url = self.tech_01_upd['url']
        tech_01.flg_xfel_available = self.tech_01_upd['flg_xfel_available']
        tech_01.flg_available = self.tech_01_upd['flg_available']
        tech_01.description = self.tech_01_upd['description']
        result6 = tech_01.update()
        self.assert_update_success(MODULE_NAME, result6, self.tech_01_upd)

        #
        # Put entry information (update some fields should throw an error)
        #
        tech_01.name = '_______THIS_NAME_IS_1_CHARACTERS_LONGER_THAN_THE_MAX_80_ALLOWED_CHARACTERS_______'  # noqa
        tech_01.identifier = self.tech_01_upd['identifier']
        tech_01.url = self.tech_01_upd['url']
        tech_01.flg_xfel_available = self.tech_01_upd['flg_xfel_available']
        tech_01.flg_available = self.tech_01_upd['flg_available']
        tech_01.description = self.tech_01_upd['description']
        result7 = tech_01.update()
        expect_app_info = {'name': ['is too long (maximum is 80 characters)']}
        self.assert_update_error(MODULE_NAME, result7, expect_app_info)

        #
        # Delete entry (should succeed)
        # (test purposes only to keep the DB clean)
        #
        result8 = tech_01.delete()
        self.assert_delete_success(MODULE_NAME, result8)

        #
        # Delete entry (should throw an error)
        # (test purposes only to keep the DB clean)
        #
        result9 = tech_01.delete()
        self.assert_delete_error(MODULE_NAME, result9, RESOURCE_NOT_FOUND)

    #
    # fields_validation
    #
    def fields_validation(self, receive, expect):
        self.assert_eq_hfield(receive, expect, 'name', STRING)
        self.assert_eq_hfield(receive, expect, 'identifier', STRING)
        self.assert_eq_hfield(receive, expect, 'url', STRING)
        self.assert_eq_hfield(receive, expect, 'flg_xfel_available', BOOLEAN)
        self.assert_eq_hfield(receive, expect, 'flg_available', BOOLEAN)
        self.assert_eq_hfield(receive, expect, 'description', STRING)


if __name__ == '__main__':
    unittest.main()
