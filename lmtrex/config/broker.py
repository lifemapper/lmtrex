"""This module provides REST services for service objects.  It should be installed into
"""
import cherrypy
# import cherrypy_cors

from lmtrex.config.local_constants import SCRATCH_PATH
from lmtrex.services.api.v1.map import MapSvc
from lmtrex.services.api.v1.name import NameSvc
from lmtrex.services.api.v1.occ import OccurrenceSvc
from lmtrex.services.api.v1.badge import BadgeSvc
from lmtrex.services.api.v1.frontend import FrontendSvc
from lmtrex.services.api.v1.stats import StatsSvc
from lmtrex.services.api.v1.address import AddressSvc

from lmtrex.common.lmconstants import (CHERRYPY_CONFIG_FILE)

# .............................................................................
def CORS():
    """This function enables Cross-Origin Resource Sharing (CORS)
    for a web request.

    Function to be called before processing a request.  This will add response
    headers required for CORS (Cross-Origin Resource Sharing) requests.  This
    is needed for browsers running JavaScript code from a different domain.
    """
    cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'
    cherrypy.response.headers[
        'Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
    cherrypy.response.headers['Access-Control-Allow-Headers'] = '*'
    cherrypy.response.headers['Access-Control-Allow-Credentials'] = 'true'
    if cherrypy.request.method.lower() == 'options':
        cherrypy.response.headers['Content-Type'] = 'text/plain'
        return 'OK'
    
# .............................................................................
def start_cherrypy_services():
    conf = {
        '/': {'request.dispatch': cherrypy.dispatch.MethodDispatcher()} 
        }
    # .............................................................................
    # Tell CherryPy to add headers needed for CORS
#     cherrypy_cors.install()
#     cherrypy.config.update(CHERRYPY_CONFIG_FILE)
    cherrypy.tools.CORS = cherrypy.Tool('before_handler', CORS)
    cherrypy.config.update(
        {'server.socket_port': 8080,
         'log.error_file': '/Users/maxxxxxdlp/.Trash/log/cherrypyErrors.log'.format(SCRATCH_PATH),
         'log.access_file': '/Users/maxxxxxdlp/.Trash/log/cherrypyAccess.log'.format(SCRATCH_PATH),
         'response.timeout': 1000000,
         'tools.CORS.on': True,
         'tools.encode.encoding': 'utf-8',
         'tools.encode.on': True,
         'tools.etags.autotags': True,
         'tools.sessions.on': True,
         'tools.sessions.storage_class': cherrypy.lib.sessions.FileSession,
         'tools.sessions.storage_path': '/Users/maxxxxxdlp/.Trash/sessions'.format(SCRATCH_PATH),
         '/static': {
             'tools.staticdir.on': True,
             'cors.expose.on': True
             }
         })
    cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'

    # ARK service
    cherrypy.tree.mount(AddressSvc(), AddressSvc.endpoint(), conf)

    # Occurrence services, by GUID, by parameters (i.e. dataset_key, ...)
    cherrypy.tree.mount(OccurrenceSvc(), OccurrenceSvc.endpoint(), conf)

    # Map services
    cherrypy.tree.mount(MapSvc(), MapSvc.endpoint(), conf)

    # Name services
    cherrypy.tree.mount(NameSvc(), NameSvc.endpoint(), conf)
    
    # Badge services
    cherrypy.tree.mount(BadgeSvc(), BadgeSvc.endpoint(), conf)

    # Frontend services
    cherrypy.tree.mount(FrontendSvc(), FrontendSvc.endpoint(), conf)

    # Stats services
    cherrypy.tree.mount(StatsSvc(), StatsSvc.endpoint(), conf)


# .............................................................................
if __name__ == '__main__':
    """
    Example calls:
        curl http://129.237.201.192/api/v1/occ/2c1becd5-e641-4e83-b3f5-76a55206539a
    """
    start_cherrypy_services()
    
    # If we are starting cherrypy directly...
    cherrypy.engine.start()
    cherrypy.engine.block()
