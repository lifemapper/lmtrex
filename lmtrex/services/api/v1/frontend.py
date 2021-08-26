import cherrypy

from lmtrex.tools.utils import get_traceback
from lmtrex.common.lmconstants import (APIService)
from lmtrex.services.api.v1.base import _S2nService
from lmtrex.services.api.v1.occ import OccurrenceSvc
from lmtrex.services.api.v1.name import NameSvc
from lmtrex.frontend.templates import template, index_template
from lmtrex.frontend.leaflet import leaflet
from lmtrex.frontend.response_to_table import response_to_table
from lmtrex.frontend.format_table import table_data_to_html
from lmtrex.frontend.format_value import serialize_response

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
            good_params, errors = self._standardize_params(
                namestr=namestr,
                occid=occid
            )
        except Exception:
            traceback = get_traceback()
            return self.get_failure(
                query_term=namestr,
                errors=[{ 'error': traceback }]
            )

        if not good_params['occid']:
            good_params['occid'] = None

        if not good_params['namestr']:
            good_params['namestr'] = None

        if good_params['occid'] is None and good_params['namestr'] is None:
            cherrypy.response.status = 400
            return index_template(
                'Invalid request URL'
            )

        occurrence_info = [
            {
                'internal:service': response['service'],
                'internal:provider': response['provider'],
                **response['records'][0]
            }
            for response in serialize_response(
                OccurrenceSvc().GET(occid=good_params['occid'])['records']
            )
            if len(response['records'])>0
        ] if good_params['occid'] else []

        scientific_names = [
            response['dwc:scientificName']
            for response in occurrence_info
            if 'dwc:scientificName' in response
        ]
        scientific_name = scientific_names[0] \
            if len(scientific_names)>0 else good_params['namestr']

        name_info = [
            {
                'internal:service': response['service'],
                'internal:provider': response['provider'],
                **response['records'][0]
            }
            for response in serialize_response(
                NameSvc().GET(namestr=scientific_name)['records']
            )
            if len(response['records']) > 0
        ] if scientific_name else []

        issues = {}
        for response in occurrence_info:
            if 's2n:issues' not in response:
                continue

            provider_issues = response['s2n:issues']
            if not provider_issues:
                continue

            label = response['internal:provider']['label']
            formatted_issues = [
                f'{message} ({key})'
                for key, message in provider_issues.items()
            ]
            issues[label] = formatted_issues

        header_row, rows = response_to_table(occurrence_info)
        occurrence_table = table_data_to_html(
            header_row,
            rows,
            'Occurrence data'
        )

        if issues:
            occurrence_table = template(
                'issues',
                dict(
                    issues=[
                        template(
                            'issue_block',
                            dict(
                                label=label,
                                provider_issues=[
                                    template('li',dict(content=issue))
                                    for issue in provider_issues
                                ]
                            )
                        )
                        for label, provider_issues in issues.items()
                    ],
                    occurrence_table=occurrence_table
                )
            )

        header_row, rows = response_to_table(name_info)
        name_table = table_data_to_html(
            header_row,
            rows,
            'Species data'
        )

        leaflet_map_data = leaflet(occurrence_info, name_info, scientific_name)
        leaflet_map_section = \
            template('section', leaflet_map_data) \
            if leaflet_map_data \
            else ''

        sections = [
            section
            for section in [
                occurrence_table,
                name_table,
                leaflet_map_section
            ]
            if section
        ]

        if len(sections) == 0:
            cherrypy.response.status = 404
            return index_template(
                'Unable to find any information for this record'
            )

        return index_template(
            template(
                'layout',
                dict(
                    title=scientific_name if \
                        scientific_name \
                        else 'Scientific Name Unknown',
                    sections=sections
                )
            )
        )


# .............................................................................
if __name__ == '__main__':
    from lmtrex.common.lmconstants import TST_VALUES
    svc = FrontendSvc()
    print(svc.GET(occid=TST_VALUES.GUIDS_W_SPECIFY_ACCESS[0]))
