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

        show_loader = 'loader' not in kwargs or kwargs['loader']!='false'

        if show_loader:
            return index_template('')

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
            return template(
                'error',
                dict(body='Invalid request URL')
            )

        occurrence_info = [
            {
                'internal:service': response['service'],
                'internal:provider': response['provider'],
                **response['records'][0],
                # 'mopho:specimen.specimen_id':
            }
            for response in serialize_response(
                OccurrenceSvc().GET(occid=good_params['occid'])['records']
            )
            if len(response['records'])>0
        ] if good_params['occid'] else []

        morpho_source_responses = [
            response
            for response in occurrence_info
            if response['internal:provider']['code'] == 'mopho'
        ]
        if morpho_source_responses:
            morpho_source_response = response_to_table(
                morpho_source_responses)
            occurrence_info = [
                {
                    **response,
                    'mopho:specimen.specimen_id':
                        response['mopho:specimen.specimen_id']
                        if response['mopho:specimen.specimen_id']
                        else morpho_source_response[0][0]['view_url']
                } for response in occurrence_info
            ]

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

        issues = []
        for response in occurrence_info:
            if 's2n:issues' not in response:
                continue

            provider_issues = response['s2n:issues']
            if not provider_issues:
                continue

            issues.append({
                'provider':response['internal:provider'],
                'issues': [
                    f'{message} ({key})'
                    for key, message in provider_issues.items()
                ]
            })

        occurrence_info = [
            response
            for response in occurrence_info
            if response['internal:provider']['code'] != 'mopho'
        ]

        header_row, rows = response_to_table(occurrence_info)
        occurrence_table = table_data_to_html(
            header_row,
            rows,
        )

        issues_section=template(
            'section',
            dict(
                label='Data Quality',
                anchor='issues',
                content=[
                    template(
                        'subsection',
                        dict(
                            label=(
                                "Reported by "
                                f"{issue_block['provider']['label']}"
                            ),
                            anchor=f"issues_{issue_block['provider']['code']}",
                            content=template(
                                'ul',
                                dict(
                                    items=[
                                        template('li', dict(content=issue))
                                        for issue in issue_block['issues']
                                    ]
                                )
                            )
                        )
                    )
                    for issue_block in issues
                ]
            )
        ) if issues else ''

        occurrence_section = template(
            'section',
            dict(
                anchor='occ',
                label='Collection Object',
                content=occurrence_table
            )
        ) if occurrence_table else ''


        header_row, rows = response_to_table(name_info)
        name_table = table_data_to_html(
                    header_row,
                    rows
                )
        name_section = template(
            'section',
            dict(
                anchor='name',
                label='Taxonomy',
                content=name_table
            )
        ) if name_table else ''

        leaflet_map_section = leaflet(occurrence_info, name_info, scientific_name)

        sections = [
            section
            for section in [
                issues_section,
                occurrence_section,
                name_section,
                leaflet_map_section
            ]
            if section
        ]

        if len(sections) == 0 or not scientific_name:
            cherrypy.response.status = 404
            return template(
                'error',
                dict(body='Unable to find any information for this record')
            )

        return template(
            'layout',
            dict(
                title=scientific_name if \
                    scientific_name \
                    else 'Scientific Name Unknown',
                sections=sections
            )
        )


# .............................................................................
if __name__ == '__main__':
    from lmtrex.common.lmconstants import TST_VALUES
    svc = FrontendSvc()
    print(svc.GET(occid=TST_VALUES.GUIDS_W_SPECIFY_ACCESS[0]))
