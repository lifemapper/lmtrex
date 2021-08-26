import cherrypy
from http import HTTPStatus
import os

from lmtrex.common.lmconstants import (
    IMG_PATH, ServiceProvider, APIService, ICON_CONTENT)
from lmtrex.common.s2n_type import S2nKey

from lmtrex.tools.utils import get_traceback

from lmtrex.services.api.v1.base import _S2nService


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
        # ITIS
        elif provider == ServiceProvider.ITISSolr[S2nKey.PARAM]:
            fname = ServiceProvider.ITISSolr['icon'][icon_status]
        # Lifemapper
        elif provider == ServiceProvider.Lifemapper[S2nKey.PARAM]:
            fname = ServiceProvider.Lifemapper['icon'][icon_status]
        # MorphoSource
        elif provider == ServiceProvider.MorphoSource[S2nKey.PARAM]:
            fname = ServiceProvider.MorphoSource['icon'][icon_status]
        # Specify
        elif provider == ServiceProvider.Specify[S2nKey.PARAM]:
            fname = ServiceProvider.Specify['icon'][icon_status]
        # Not yet defined
        else:
            return None
            
        return os.path.join(IMG_PATH, fname)

    # ...............................................
    def get_error_or_iconfile(self, provider, icon_status):
        icon_fname = None
        error_description = None
        http_status = int(HTTPStatus.OK)
        try:
            good_params, errinfo = self._standardize_params(
                provider=provider, icon_status=icon_status)
            # Bad parameters
            try:
                error_description = '; '.join(errinfo['error'])                            
                http_status = int(HTTPStatus.BAD_REQUEST)
            except:
                pass
                
        except Exception as e:
            # Unknown error
            http_status = int(HTTPStatus.INTERNAL_SERVER_ERROR)
            error_description = get_traceback()
            
        else:
            if http_status != HTTPStatus.BAD_REQUEST:
                icon_status = good_params['icon_status']
                provider = good_params['provider']                
                # Find file!
                try:
                    icon_fname = self.get_icon(provider, icon_status)
                except Exception as e:
                    http_status = int(HTTPStatus.INTERNAL_SERVER_ERROR)
                    error_description = get_traceback()
                else:
                    if not icon_fname:
                        http_status = int(HTTPStatus.NOT_IMPLEMENTED)
                        error_description = 'Badge {} not implemented for provider {}'.format(
                            icon_status, provider)                        
                
        return icon_fname, http_status, error_description


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
            provider: string containing a single provider code.
            icon_status: string indicating which version of the icon to return, valid options are:
                lmtrex.common.lmconstants.VALID_ICON_OPTIONS (active, inactive, hover) 
            stream: If true, return a generator for streaming output, else return
                file contents
            kwargs: any additional keyword arguments are ignored

        Return:
            a file containing the requested icon
        """
        valid_providers = self.get_valid_providers()
        
        # return info for empty request
        if provider is None and icon_status is None:
            msg_output = self._show_online(valid_providers)
            boutput = self.get_json_service_info(msg_output)
            return boutput
        
        # return image or error for icon request
        else:
            icon_fname, http_status, error_description = self.get_error_or_iconfile(
                provider, icon_status)
        if http_status == HTTPStatus.OK:
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
            # Failed
            raise cherrypy.HTTPError(http_status, error_description)

    

# .............................................................................
if __name__ == '__main__':
    svc = BadgeSvc()
    # Get all providers
    valid_providers = svc.get_valid_providers()
    # retval = svc.GET(provider='gbif', icon_status='active')
    # print(retval)
    retval = svc.GET()
    print(retval)
    retval = svc.GET(provider='itis', icon_status='active')
    print(retval)
    try:
        retval = svc.GET(provider='morphosource', icon_status='active')
        print(retval)
    except:
        print('Failed correctly')
    retval = svc.GET(provider='mopho', icon_status='active')
    print(retval)
    # for pr in valid_providers:
    #     for stat in VALID_ICON_OPTIONS:
    #         retval = svc.GET(provider=pr, icon_status=stat)
    #         print(retval)
    