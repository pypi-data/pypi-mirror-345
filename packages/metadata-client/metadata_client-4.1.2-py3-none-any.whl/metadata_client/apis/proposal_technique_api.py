"""ProposalTechniqueApi module class"""

from ..common.base import Base
from ..common.config import *


class ProposalTechniqueApi(Base):
    def get_proposal_technique_by_proposal_id_api(self, proposal_id,
                                                  page=DEF_PAGE,
                                                  page_size=DEF_PAGE_SIZE):
        api_url = self.__get_api_url()
        return self.api_get(api_url, params={'proposal_id': proposal_id,
                                             'page': page,
                                             'page_size': page_size})

    def get_proposal_technique_by_technique_id_api(self, technique_id,
                                                   page=DEF_PAGE,
                                                   page_size=DEF_PAGE_SIZE):
        api_url = self.__get_api_url()
        return self.api_get(api_url, params={'technique_id': technique_id,
                                             'page': page,
                                             'page_size': page_size})

    #
    # Private Methods
    #
    def __get_api_url(self, api_specifics=''):
        model_name = 'proposals_techniques/'
        return self.get_api_url(model_name, api_specifics)
