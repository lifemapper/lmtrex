import cherrypy

from lmtrex.tools.utils import get_traceback
from lmtrex.common.lmconstants import (APIService)
import json
from lmtrex.services.api.v1.base import _S2nService
from lmtrex.services.api.v1.occ import OccurrenceSvc
from lmtrex.services.api.v1.name import NameSvc
from lmtrex.services.api.v1.map import MapSvc
from lmtrex.frontend.json_to_html import json_to_html
from lmtrex.frontend.templates import template, index_template

# .............................................................................
@cherrypy.expose
class FrontendSvc(_S2nService):
    SERVICE_TYPE = APIService.Frontend

    # ...............................................
    # ...............................................
    def GET(self, occid=None, namestr=None, **kwargs):
        """Front end for the broker services

        Aggregate the results from badge, occ, name and map endpoints into a
        single web page.

        Args:
            occid: an occurrenceID, a DarwinCore field intended for a globally
                unique identifier (https://dwc.tdwg.org/list/#dwc_occurrenceID)
            kwargs: any additional keyword arguments are ignored

        Return:
            Responses from all agregators formatted as an HTML page
        """

        try:
            usr_params = self._standardize_params(
                occid=occid, namestr=namestr
            )
        except Exception:
            traceback = get_traceback()
            return self.get_failure(
                query_term=occid, errors=[traceback]
            ).response

        occurrence_info = [
            {
                's2n:provider': response['provider'],
                **response['records'][0]
            }
            for response in \
                OccurrenceSvc().GET(occid=usr_params['occid'])['records']
            if len(response['records'])>0 and \
                 'dwc:scientificName' in response['records'][0]
        ]

        if len(occurrence_info) == 0:
            scientific_name = namestr
        else:
            scientific_name = [
                response['dwc:scientificName']
                for response in occurrence_info
            ][0]

        if not scientific_name:
            cherrypy.response.status = 404
            return index_template(
                'Unable to find any information for this record'
            )

        name_info = [
            {
                's2n:provider': response['provider'],
                **response['records'][0]
            }
            for response in \
            NameSvc().GET(namestr=scientific_name)['records']
            if len(response['records']) > 0
        ]

        map_info = [
            response['records'][0]
            for response in \
            MapSvc().GET(namestr=scientific_name)['records']
            if len(response['records']) > 0 and \
                response['provider']=='Lifemapper'
        ]

        provider_icon_mapper = {
            'Lifemapper': 'lm',
            'Morpho': 'mopho',
            'GBIF': 'gbif',
            'iDigBio': 'idb',
            'ITIS': '',
        }

        sections = []

        for response in occurrence_info:
            sections.append({
                'icon_url':
                    f'https://broker-dev.spcoco.org/api/v1/badge/?provider='
                    f'{provider_icon_mapper[response["s2n:provider"]]}'
                    f'&icon_status=active',
                'label': response["s2n:provider"],
                'content': json_to_html(response)
            })

        for response in name_info:
            sections.append({
                'icon_url':
                    f'https://broker-dev.spcoco.org/api/v1/badge/?provider='
                    f'{provider_icon_mapper[response["s2n:provider"]]}'
                    f'&icon_status=active',
                'label': response["s2n:provider"],
                'content': json_to_html(response)
            })

        return index_template(
            template(
                'layout',
                dict(
                    title=scientific_name,
                    sections=''.join([
                        template('section', section)
                        for section in sections
                    ])
                )
            )
        )


# .............................................................................
if __name__ == '__main__':
    from lmtrex.common.lmconstants import TST_VALUES
    svc = FrontendSvc()
    print(svc.GET(occid=TST_VALUES.GUIDS_W_SPECIFY_ACCESS[0]))
