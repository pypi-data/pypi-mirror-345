"""ReportApi module class"""

import json

from ..common.base import Base
from ..common.config import *


class ReportApi(Base):
    def create_report_api(self, report):
        api_url = self.__get_api_url()
        return self.api_post(api_url, data=json.dumps(report))

    def delete_report_api(self, report_id):
        api_url = self.__get_api_url(report_id)
        return self.api_delete(api_url)

    def update_report_api(self, report_id, report):
        api_url = self.__get_api_url(report_id)
        return self.api_put(api_url, data=json.dumps(report))

    def get_report_by_id_api(self, report_id):
        api_url = self.__get_api_url(report_id)
        return self.api_get(api_url, params={})

    def get_all_reports_api(self, page=DEF_PAGE, page_size=DEF_PAGE_SIZE):
        api_url = self.__get_api_url()
        return self.api_get(api_url, params={'page': page,
                                             'page_size': page_size})

    def get_all_reports_by_run_id_api(self, run_id,
                                      page=DEF_PAGE,
                                      page_size=DEF_PAGE_SIZE):
        api_url = self.__get_api_url()
        return self.api_get(api_url, params={'run_id': run_id,
                                             'page': page,
                                             'page_size': page_size})

    #
    # Private Methods
    #
    def __get_api_url(self, api_specifics=''):
        model_name = 'reports/'
        return self.get_api_url(model_name, api_specifics)
