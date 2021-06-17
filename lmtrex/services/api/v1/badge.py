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
        if provider is None or icon_status is None:
            output = self._show_online(valid_providers)
        elif provider.lower() in APIService.get_other_endpoints(self.SERVICE_TYPE):
            output = self._show_online(valid_providers)
        else:
            try:
                usr_params, info_valid_options = self._standardize_params_new(
                    provider=provider, icon_status=icon_status)
            except Exception as e:
                traceback = get_traceback()
                output = self.get_failure(query_term='provider={}, icon_status={}'.format(
                    provider, icon_status), errors=[{'error': traceback}])
            else:
                # Without a provider or icon_status, send online status
                if len(usr_params['provider']) == 0 or usr_params['icon_status'] is None:
                    output = self._show_online(valid_providers)
                else:
                    # Only first provider is used
                    provider = usr_params['provider'].pop()
                    icon_status = usr_params['icon_status']
                    try:
                        icon_fname = self.get_icon(provider, icon_status)
                    except Exception as e:
                        traceback = get_traceback()
                        output = self.get_failure(query_term='provider={}, icon_status={}'.format(
                            provider, icon_status), errors=[{'error': traceback}])

        # Return service parameters if anything is amiss
        if output:
            return output.response
        else:
            # Whew
            ifile = open(icon_fname, mode='rb')
            # ret_file_name = os.path.basename(icon_fname)
            # cherrypy.response.headers[
            #     'Content-Disposition'] = 'attachment; filename="{}"'.format(ret_file_name)
            cherrypy.response.headers['Content-Type'] = ICON_CONTENT
            
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
    retval = svc.GET(provider='gbif', icon_status='activex')
    print(retval)
    retval = svc.GET()
    print(retval)
    retval = svc.GET(provider='gbif', icon_status='active')
    print(retval)
    # for pr in valid_providers:
    #     for stat in VALID_ICON_OPTIONS:
    #         retval = svc.GET(provider=pr, icon_status=stat)
    #         print(retval)
    