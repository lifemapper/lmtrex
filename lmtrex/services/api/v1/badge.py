import cherrypy
import os

from lmtrex.common.lmconstants import (
    IMG_PATH, ServiceProvider, APIService, ICON_CONTENT)

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
        output = None
        
        valid_providers = self.get_valid_providers()
        if provider is None and icon_status is None:
            output = self._show_online(valid_providers)
        elif provider.lower() in APIService.get_other_endpoints(self.SERVICE_TYPE):
            output = self._show_online(valid_providers)
        else:
            try:
                good_params, option_errors = self._standardize_params_new(
                    provider=provider, icon_status=icon_status)
            except Exception as e:
                traceback = get_traceback()
                output = self.get_failure(query_term='provider={}, icon_status={}'.format(
                    provider, icon_status), errors=[{'error': traceback}])
            else:
                errors = []
                try:
                    provider = good_params['provider'].pop()
                except:
                    errors.append(
                         {'error': 
                          'Parameter provider containing one of {} options is required'.format(
                              valid_providers)})
                else:                    
                    if provider not in valid_providers:
                        errors.append(
                             {'error': 
                              'Value(s) {} for parameter provider not in valid options {}'.format(
                                  good_params['provider'], valid_providers)})
                    if option_errors:
                        errors.extend(option_errors)
                        
                    if errors:
                        output = self.get_failure(provider=','.join(valid_providers), errors=errors)
                    else:
                        # Only first provider is used
                        provider = good_params['provider'].pop()
                        icon_status = good_params['icon_status']
                        try:
                            icon_fname = self.get_icon(provider, icon_status)
                        except Exception as e:
                            traceback = get_traceback()
                            output = self.get_failure(query_term='provider={}, icon_status={}'.format(
                                provider, icon_status), errors=[{'error': traceback}])

        # Return service parameters if anything is amiss
        if output:
            boutput = self.get_json_service_info(output)
            return boutput
            
        else:
            cherrypy.response.headers['Content-Type'] = ICON_CONTENT
            ifile = open(icon_fname, mode='rb')
            if stream:
                return cherrypy.lib.file_generator(ifile)
            else:
                icontent = ifile.read()
                ifile.close()
                return icontent
    

# .............................................................................
if __name__ == '__main__':
    svc = BadgeSvc()
    # Get all providers
    valid_providers = svc.get_valid_providers()
    retval = svc.GET(provider='gbif')
    print(retval)
    retval = svc.GET()
    print(retval)
    retval = svc.GET(provider='morphosource', icon_status='active')
    print(retval)
    # for pr in valid_providers:
    #     for stat in VALID_ICON_OPTIONS:
    #         retval = svc.GET(provider=pr, icon_status=stat)
    #         print(retval)
    