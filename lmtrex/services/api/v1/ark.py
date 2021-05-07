import cherrypy

from lmtrex.common.lmconstants import (ServiceProvider, APIService, SPECIFY)
import lmtrex.tools.solr as SpSolr
from lmtrex.tools.utils import get_traceback

collection = 'spcoco'
solr_location = 'notyeti-192.lifemapper.org'

# .............................................................................
@cherrypy.expose
class ResolveSvc(_S2nService):
    """Query the Specify Resolver with a UUID for a resolvable GUID and URL"""
    SERVICE_TYPE = APIService.Resolve
    


    # ...............................................
    def put_records(self, fname, collection):
        allrecs = []

        
    # ...............................................
    @cherrypy.tools.json_out()
    def POST(self, fname=None, collection=None, **kwargs):
        """Accept a file for posting to solr collection.
        
        Args:
            fname: an occurrenceID, a DarwinCore field intended for a globally 
                unique identifier (https://dwc.tdwg.org/list/#dwc_occurrenceID)
            kwargs: any additional keyword arguments are ignored

        Return:
            A dictionary of metadata and a count of records found in GBIF and 
            an optional list of records.
                
        Note: 
            There will never be more than one record returned.
        """
        pass


# .............................................................................
if __name__ == '__main__':
    # test
    from lmtrex.common.lmconstants import TST_VALUES
    
