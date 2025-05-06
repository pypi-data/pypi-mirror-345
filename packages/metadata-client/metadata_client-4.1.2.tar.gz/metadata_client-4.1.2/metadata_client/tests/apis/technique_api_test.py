"""TechniqueApiTest class"""

import unittest

from metadata_client import MetadataClient
from .api_base import ApiBase
from ..common.config_test import *
from ..common.secrets import *


class TechniqueApiTest(ApiBase, unittest.TestCase):
    client_api = MetadataClient(
        client_id=CLIENT_OAUTH2_INFO['CLIENT_ID'],
        client_secret=CLIENT_OAUTH2_INFO['CLIENT_SECRET'],
        token_url=CLIENT_OAUTH2_INFO['TOKEN_URL'],
        refresh_url=CLIENT_OAUTH2_INFO['REFRESH_URL'],
        auth_url=CLIENT_OAUTH2_INFO['AUTH_URL'],
        scope=CLIENT_OAUTH2_INFO['SCOPE'],
        user_email=CLIENT_OAUTH2_INFO['EMAIL'],
        base_api_url=BASE_API_URL)

    def test_create_technique_api(self):
        technique_func = {
            'technique': {
                'name': 'Functional Tests Technique 01 (DO NOT CHANGE)',
                'identifier': 'TECHNIQUE-TEST-1',
                'url': 'https://in.xfel.eu/TECH1',
                'flg_available': True,
                'flg_xfel_available': True,
                'description': 'Technique used by upex and metadata client '
                               'library for functional tests.'
            }
        }

        expect = technique_func['technique']

        #
        # Get entry by identifier
        #
        self.__get_all_entries_by_identifier_api('TECHNIQUE-TEST-1', expect)

        #
        # Get entry by name
        #
        self.__get_all_entries_by_name_api(
            'Functional Tests Technique 01 (DO NOT CHANGE)', expect)

        #
        # Get entry by ID
        #
        technique_id = -1
        self.__get_entry_by_id_api(technique_id, expect)

    #
    # fields_validation
    #
    def fields_validation(self, receive, expect):
        self.assert_eq_hfield(receive, expect, 'name', STRING)
        self.assert_eq_hfield(receive, expect, 'identifier', STRING)
        self.assert_eq_hfield(receive, expect, 'url', STRING)
        self.assert_eq_hfield(receive, expect, 'flg_available', BOOLEAN)
        self.assert_eq_hfield(receive, expect, 'flg_xfel_available', BOOLEAN)
        self.assert_eq_hfield(receive, expect, 'description', STRING)

    #
    # Internal private APIs methods
    #
    def __get_all_entries_by_identifier_api(self, identifier, expect):
        response = self.client_api.get_all_techniques_by_identifier_api(
            identifier)
        receive = self.get_and_validate_all_entries_by_name(response)
        self.fields_validation(receive, expect)

    def __get_all_entries_by_name_api(self, identifier, expect):
        response = self.client_api.get_all_techniques_by_name_api(
            identifier)
        receive = self.get_and_validate_all_entries_by_name(response)
        self.fields_validation(receive, expect)

    def __get_entry_by_id_api(self, entry_id, expect):
        response = self.client_api.get_technique_by_id_api(entry_id)
        receive = self.get_and_validate_entry_by_id(response)
        self.fields_validation(receive, expect)


if __name__ == '__main__':
    unittest.main()
