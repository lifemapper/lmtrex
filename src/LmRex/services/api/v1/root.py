"""This module provides REST services for service objects"""
import cherrypy
# import cherrypy_cors

from LmRex.services.api.v1.lifemapper import LmMap
from LmRex.services.api.v1.name import (
    GAcName, ITISName, ITISSolrName, NameTentaclesSvc)
from LmRex.services.api.v1.occ import (
    GOcc, GColl, IDBOcc, MophOcc, SPOcc, OccTentaclesSvc)
from LmRex.services.api.v1.sparks import SpecifyArk

from LmRex.common.lmconstants import (APIMount, CHERRYPY_CONFIG_FILE)

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
    cherrypy.tools.CORS = cherrypy.Tool('before_handler', CORS)
#     cherrypy.config.update(CHERRYPY_CONFIG_FILE)
    cherrypy.config.update(
        {'server.socket_port': 80,
         'server.socket_host': '129.237.201.192',
         'log.error_file': '/state/partition1/lmscratch/log/cherrypyErrors.log',
         'log.access_file': '/state/partition1/lmscratch/log/cherrypyAccess.log',
         'response.timeout': 1000000,
         'tools.CORS.on': True,
         'tools.encode.encoding': 'utf-8',
         'tools.encode.on': True,
         'tools.etags.autotags': True,
         'tools.sessions.on': True,
         'tools.sessions.storage_class': cherrypy.lib.sessions.FileSession,
         'tools.sessions.storage_path': '/state/partition1/lmscratch/sessions',
         '/static': {
             'tools.staticdir.on': True,
             'cors.expose.on': True
             }
         })

    cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'
    
    # ARK service
    cherrypy.tree.mount(SpecifyArk(), APIMount.SpecifyArkSvc, conf)

    # Occurrence services
    cherrypy.tree.mount(OccTentaclesSvc(), APIMount.OccTentaclesSvc, conf)
    cherrypy.tree.mount(GOcc(), APIMount.GOccSvc, conf)
    cherrypy.tree.mount(IDBOcc(), APIMount.IDBOccSvc, conf)
    cherrypy.tree.mount(MophOcc(), APIMount.MophOccSvc, conf)
    cherrypy.tree.mount(SPOcc(), APIMount.SPOccSvc, conf)
    # Occurrence by dataset
    cherrypy.tree.mount(GColl(), APIMount.GCollSvc, conf)
    # Map services
    cherrypy.tree.mount(LmMap(), APIMount.LmMapSvc, conf)
    # Name services
    cherrypy.tree.mount(NameTentaclesSvc(), APIMount.NameTentaclesSvc, conf)
    cherrypy.tree.mount(GAcName(), APIMount.GAcNameSvc, conf)
    cherrypy.tree.mount(ITISSolrName(), APIMount.ITISSolrNameSvc, conf)   

    cherrypy.engine.start()
    cherrypy.engine.block()

# .............................................................................
if __name__ == '__main__':
    """
    Example calls:
        curl http://129.237.201.192/sparks/2c1becd5-e641-4e83-b3f5-76a55206539a
        curl http://129.237.201.192/api/v1/occ/idb/2c1becd5-e641-4e83-b3f5-76a55206539a
    """
    start_cherrypy_services()
    