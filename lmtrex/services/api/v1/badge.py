import cherrypy

from lmtrex.common.lmconstants import (ServiceProvider, APIService, ICON_OPTIONS)

from lmtrex.tools.utils import get_traceback

from lmtrex.services.api.v1.base import _S2nService
from lmtrex.services.api.v1.s2n_type import S2nKey

# .............................................................................
@cherrypy.expose
# @cherrypy.popargs('path_occ_id')
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
        # MorphoSource
        elif provider == ServiceProvider.MorphoSource[S2nKey.PARAM]:
            fname = ServiceProvider.MorphoSource['icon'][icon_status]
        # Lifemapper
        elif provider == ServiceProvider.Specify[S2nKey.PARAM]:
            fname = ServiceProvider.Specify['icon'][icon_status]

        return fname

    # ...............................................
    # ...............................................
    @cherrypy.tools.json_out()
    def GET(self, provider=None, icon_status=None, **kwargs):
        """Get one icon to indicate a provider in a GUI
        
        Args:
            provider: string containing a comma delimited list of provider codes.  The icon 
                for only the first provider will be returned.  If the string is not present
                or 'all', the first provider in the default list of providers will be returned.
            icon_status: string indicating which version of the icon to return, valid options are:
                lmtrex.common.lmconstants.ICON_OPTIONS (active, inactive, hover) 
            kwargs: any additional keyword arguments are ignored

        Return:
            a file containing the requested icon
        """
        try:
            usr_params = self._standardize_params(provider=provider, icon_status=icon_status)
        except Exception as e:
            traceback = get_traceback()
            retval = traceback
        else:
            # Who to query
            valid_providers = self.get_providers()
            valid_req_providers, invalid_providers = self.get_valid_requested_providers(
                usr_params['provider'], valid_providers)
            provider = valid_req_providers[0]
            
            # What to query: address one occurrence record, with optional filters
            icon_status = usr_params['icon_status']
            try:
                if icon_status is None:
                    output = self._show_online(providers=valid_req_providers)
                    retval = output.response
                else:
                    icon_fname = self.get_icon(provider, icon_status)
                    retval = icon_fname
            except Exception as e:
                traceback = get_traceback()
                retval = traceback
        return retval
    

# .............................................................................
if __name__ == '__main__':
    svc = BadgeSvc()
    # Get all providers
    valid_providers = svc.get_providers()
    for pr in valid_providers:
        for stat in ICON_OPTIONS:
            icon = svc.GET(provider=pr, icon_status=stat)
            print 
    