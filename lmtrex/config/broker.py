"""This module provides REST services for service objects.  It should be installed into
"""
import cherrypy
import os

from lmtrex.services.api.v1.map import MapSvc
from lmtrex.services.api.v1.name import NameSvc
from lmtrex.services.api.v1.occ import OccurrenceSvc
from lmtrex.services.api.v1.badge import BadgeSvc
from lmtrex.services.api.v1.frontend import FrontendSvc
from lmtrex.services.api.v1.stats import StatsSvc
from lmtrex.services.api.v1.address import AddressSvc

# .............................................................................
def start_cherrypy_services():
    conf = {
        '/': {'request.dispatch': cherrypy.dispatch.MethodDispatcher()} 
        }

    scratch_path = '/scratch-path/'
    development = os.environ['DEVELOPMENT'] == 'true'
    cherrypy.config.update(
        {'server.socket_port': 8080,
         'server.socket_host': '0.0.0.0',
         'log.error_file': '{}/log/cherrypyErrors.log'.format(scratch_path),
         'log.access_file': '{}/log/cherrypyAccess.log'.format(scratch_path),
         'response.timeout': 1000000,
         'environment':
             None if development else 'production',
         'tools.encode.encoding': 'utf-8',
         'tools.encode.on': True,
         'tools.etags.autotags': True,
         'tools.sessions.on': True,
         'engine.autoreload.on': development,
         'tools.sessions.storage_class': cherrypy.lib.sessions.FileSession,
         'tools.sessions.storage_path': '{}/sessions'.format(scratch_path),
         '/static': {
             'tools.staticdir.on': True,
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
