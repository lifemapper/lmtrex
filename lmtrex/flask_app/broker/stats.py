import cherrypy

from lmtrex.common.lmconstants import (APIService)
from lmtrex.frontend.templates import stats_template
from lmtrex.services.api.v1.base import _S2nService


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


        return stats_template()
