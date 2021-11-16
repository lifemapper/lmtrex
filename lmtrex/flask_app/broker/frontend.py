import cherrypy

from lmtrex.common.lmconstants import (APIService)
from lmtrex.frontend.templates import frontend_template
from lmtrex.services.api.v1.base import _S2nService


# .............................................................................
@cherrypy.expose
class FrontendSvc(_S2nService):
    SERVICE_TYPE = APIService.Frontend

    # ...............................................
    # ...............................................
    def GET(self, **kwargs):
        """Front end for the broker services

        Aggregate the results from badge, occ, name and map endpoints into a
        single web page.

        Args:
            occid: an occurrenceID, a DarwinCore field intended for a globally
                unique identifier (https://dwc.tdwg.org/list/#dwc_occurrenceID)
            namestr: Species name. Used only as a fallback if failed to resolve
                occurrenceID

        Return:
            Responses from all agregators formatted as an HTML page
        """

        return frontend_template()
