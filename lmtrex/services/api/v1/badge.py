import cherrypy
from http import HTTPStatus
import os

from lmtrex.common.lmconstants import (
    BrokerParameters, IMG_PATH, ServiceProvider, APIService, ICON_CONTENT)

from lmtrex.tools.utils import get_traceback

from lmtrex.services.api.v1.base import _S2nService
from lmtrex.services.api.v1.s2n_type import S2nKey

# .............................................................................
@cherrypy.expose
class BadgeSvc(_S2nService):
    SERVICE_TYPE = APIService.Badge

    # ...............................................
    def get_icon(self, provider, icon_status):
        # GBIF
        if provider == ServiceProvider.GBIF[S2nKey.PARAM]:
            fname = ServiceProvider.GBIF['icon'][icon_status]
        # iDigBio
        elif provider == ServiceProvider.iDigBio[S2nKey.PARAM]:
            fname = ServiceProvider.iDigBio['icon'][icon_status]
        # iDigBio
        elif provider == ServiceProvider.Lifemapper[S2nKey.PARAM]:
            fname = ServiceProvider.Lifemapper['icon'][icon_status]
        # MorphoSource
        elif provider == ServiceProvider.MorphoSource[S2nKey.PARAM]:
            fname = ServiceProvider.MorphoSource['icon'][icon_status]
        # Specify
        elif provider == ServiceProvider.Specify[S2nKey.PARAM]:
            fname = ServiceProvider.Specify['icon'][icon_status]
            
        full_filename = os.path.join(IMG_PATH, fname)

        return full_filename

    # ...............................................
    def get_error_or_iconfile(self, provider, valid_providers, icon_status):
        icon_fname = error_output = None
        prov_meta = self._get_s2n_provider_response_elt()
        try:
            good_params, option_errors, is_fatal = self._standardize_params(
                provider=provider, icon_status=icon_status)
        except Exception as e:
            # query term with original user strings
            query_term='provider={}&icon_status={}'.format(provider, icon_status)
            # failed to parse parameters
            traceback = get_traceback()
            error_output = self.get_failure(
                query_term=query_term, provider=prov_meta, errors=[{'error': traceback}])
        else:
            if is_fatal:
                raise cherrypy.HTTPError(
                    HTTPStatus.BAD_REQUEST, 'Request includes one or more invalid parameters')
            else:
                icon_status = good_params['icon_status']
                provider = good_params['provider'][0]
                
                query_term='provider={}&icon_status={}'.format(provider, icon_status)    
                if not error_output and self._is_fatal(option_errors):
                    # respond to failures
                    error_output = self.get_failure(
                        query_term=query_term, provider=prov_meta, errors=option_errors)
                
                # Failed yet?
                if not error_output:
                    # Find file!
                    try:
                        icon_fname = self.get_icon(provider, icon_status)
                    except Exception as e:
                        traceback = get_traceback()
                        error_output = self.get_failure(
                            query_term=query_term, provider=prov_meta, errors=[{'error': traceback}])
                
        return icon_fname, error_output


    # ...............................................
    @cherrypy.tools.json_out()
    def get_json_service_info(self, output):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        import json
        boutput = bytes(json.dumps(output.response), 'utf-8')
        return boutput

    # ...............................................
    def GET(self, provider=None, icon_status=None, stream=True, **kwargs):
        """Get one icon to indicate a provider in a GUI
        
        Args:
            provider: string containing a comma delimited list of provider codes.  The icon 
                for only the first provider will be returned.  If the string is not present
                or 'all', the first provider in the default list of providers will be returned.
            icon_status: string indicating which version of the icon to return, valid options are:
                lmtrex.common.lmconstants.VALID_ICON_OPTIONS (active, inactive, hover) 
            stream: If true, return a generator for streaming output, else return
                file contents
            kwargs: any additional keyword arguments are ignored

        Return:
            a file containing the requested icon
        """
        icon_fname = None
        
        valid_providers = self.get_valid_providers()
        # empty query
        if provider is None and icon_status is None:
            msg_output = self._show_online(valid_providers)
        else:
            icon_fname, msg_output = self.get_error_or_iconfile(provider, valid_providers, icon_status)
            
        if icon_fname:
            # Return image data
            cherrypy.response.headers['Content-Type'] = ICON_CONTENT
            ifile = open(icon_fname, mode='rb')
            if stream:
                return cherrypy.lib.file_generator(ifile)
            else:
                icontent = ifile.read()
                ifile.close()
                return icontent
        else:
            # Must have failed
            boutput = self.get_json_service_info(msg_output)
            return boutput
    

# .............................................................................
if __name__ == '__main__':
    svc = BadgeSvc()
    # Get all providers
    valid_providers = svc.get_valid_providers()
    # retval = svc.GET(provider='gbif', icon_status='active')
    # print(retval)
    retval = svc.GET()
    print(retval)
    retval = svc.GET(provider='gbif', icon_status='active')
    print(retval)
    retval = svc.GET(provider='morphosource', icon_status='active')
    print(retval)
    # for pr in valid_providers:
    #     for stat in VALID_ICON_OPTIONS:
    #         retval = svc.GET(provider=pr, icon_status=stat)
    #         print(retval)
    