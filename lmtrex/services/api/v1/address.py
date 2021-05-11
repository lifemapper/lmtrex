import cherrypy

from lmtrex.common.lmconstants import (ServiceProvider, SPECIFY_CACHE_API, APIService)
from lmtrex.services.api.v1.base import _S2nService

# .............................................................................
@cherrypy.expose
class AddressSvc(_S2nService):
    """Query the Specify Resolver with a UUID for a resolvable GUID and URL"""
    SERVICE_TYPE = APIService.Address
    
    # ...............................................
    @cherrypy.tools.json_out()
    def GET(self, **kwargs):
        """Get address for the syftorium Specify Cache.
        
        Return:
            an API url for posting a DwCA file to be included in the Specify Cache
        """
        return SPECIFY_CACHE_API



# .............................................................................
if __name__ == '__main__':
    # test
    pass
    
