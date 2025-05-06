"""DataType module class"""

import inspect

from ..common.base import Base
from ..common.config import *

MODULE_NAME = PROPOSALS_TECHNIQUE


class ProposalTechnique:
    def __init__(self, metadata_client,
                 proposal_id, technique_id):
        self.metadata_client = metadata_client
        self.id = None
        self.proposal_id = proposal_id
        self.technique_id = technique_id

    @staticmethod
    def get_all_by_proposal_id(mdc_client, proposal_id, page=DEF_PAGE,
                               page_size=DEF_PAGE_SIZE):
        response = mdc_client.get_proposal_technique_by_proposal_id_api(
            proposal_id, page, page_size)

        curr_method_name = inspect.currentframe().f_code.co_name
        Base.cal_debug(MODULE_NAME, curr_method_name, response)
        return Base.format_response(response, GET, OK, MODULE_NAME)

    @staticmethod
    def get_all_by_technique_id(mdc_client, technique_id, page=DEF_PAGE,
                                page_size=DEF_PAGE_SIZE):
        response = mdc_client.get_proposal_technique_by_technique_id_api(
            technique_id, page, page_size)

        curr_method_name = inspect.currentframe().f_code.co_name
        Base.cal_debug(MODULE_NAME, curr_method_name, response)
        return Base.format_response(response, GET, OK, MODULE_NAME)

    def __get_resource(self):
        data_type = {
            MODULE_NAME: {
                'proposal_id': self.proposal_id,
                'technique_id': self.technique_id
            }
        }

        return data_type
