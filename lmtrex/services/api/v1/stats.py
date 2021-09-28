import cherrypy

from lmtrex.common.lmconstants import (APIService)
from lmtrex.services.api.v1.base import _S2nService
from lmtrex.frontend.templates import stats_template, template


# .............................................................................
@cherrypy.expose
class StatsSvc(_S2nService):
    SERVICE_TYPE = APIService.Stats

    # ...............................................
    # ...............................................
    def GET(self, **params):
        """Institution and collection level stats

        Return:
            HTML page that fetches and formats stats
        """


        return stats_template([
            template(
                'section',
                {
                    'label': 'Choose collection:',
                    'anchor': 'change-collection',
                    'content': template(
                        'tag',
                        {
                            'tag': 'div',
                            'children': template(
                                'tag',
                                {
                                    'tag': 'select',
                                    'children': ''
                                }
                            )
                        }
                    )
                }
            ),
            template(
                'section',
                {
                    'label': '',
                    'anchor': 'collection-distribution',
                    'content': template('leaflet-stats', { })
                }
            ),
            template(
                'section',
                {
                    'label': '',
                    'anchor': 'institution-distribution',
                    'content': template('leaflet-stats', { })
                }
            ),
        ])
