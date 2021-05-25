"""WSGI script that sits between Apache and CherryPy"""
import os
import sys
# TODO: Do this either through .in file or another config file
sys.path.append('/opt/lifemapper/')
sys.path.append('/var/www/lmtrex/')

import cherrypy

LM_ENV_VARS = ['LIFEMAPPER_LAB_CONFIG_FILE', 'LIFEMAPPER_SITE_CONFIG_FILE']


# .............................................................................
def application(environ, start_response):
    """Mod_WSGI application hook

    Args:
        environ: The mod_wsgi environment sent to the request
        start_response: _
    """
    # Set environment variables that our CherryPy application can access
    for var in LM_ENV_VARS:
        os.environ[var] = environ[var]

    # Note: Must import after we have set environment variables or it will fail
    #from lmtrex.services.api.v1.root import start_cherrypy_services
    from broker import start_cherrypy_services
    start_cherrypy_services()
    return cherrypy.tree(environ, start_response)
