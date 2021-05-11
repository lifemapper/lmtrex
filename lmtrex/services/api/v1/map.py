import cherrypy

from lmtrex.common.lmconstants import (
    ServiceProvider, APIService, Lifemapper, TST_VALUES)
from lmtrex.services.api.v1.base import _S2nService
from lmtrex.services.api.v1.s2n_type import (S2nKey, S2n, S2nOutput, print_s2n_output)
from lmtrex.tools.provider.gbif import GbifAPI
from lmtrex.tools.provider.lifemapper import LifemapperAPI
from lmtrex.tools.utils import get_traceback

# .............................................................................
@cherrypy.expose
class MapSvc(_S2nService):
    SERVICE_TYPE = APIService.Map
    
    # ...............................................
    def _match_gbif_names(self, namestr, is_accepted):
        scinames = []
        errmsgs = []
        try:
            # Get name from Gbif        
            nm_output = GbifAPI.match_name(namestr, is_accepted=is_accepted)
        except Exception as e:
            errmsgs.append('Failed to match {} to GBIF accepted name'.format(namestr))
            traceback = get_traceback()
            errmsgs.append(traceback)
            scinames.append(namestr)
        else:
            for rec in nm_output.records:
                try:
                    scinames.append(rec['scientificName'])
                except Exception as e:
                    print('No scientificName element in GBIF record {} for {}'
                          .format(rec, namestr))
        return scinames, errmsgs

    # ...............................................
    def _get_lifemapper_records(self, namestr, is_accepted, scenariocodes, color):
        errmsgs = []
        # First: get name(s)
        if is_accepted is False:
            scinames = [namestr] 
        else:
            scinames, errmsgs = self._match_gbif_names(namestr, is_accepted=is_accepted)
        # Second: get completed Lifemapper projections (map layers)
        stdrecs = []
        queries = []
        for sname in scinames:
            # TODO: search on occurrenceset, then also pull projection layers
            lout = LifemapperAPI.find_map_layers_by_name(
                sname, prjscenariocodes=scenariocodes, color=color)
            if len(lout.records) > 0:
                stdrecs.extend(lout.records)
                errmsgs.extend(lout.errors)
                queries.extend(lout.provider_query)
        query_term = 'namestr={}; is_accepted={}; scenariocodes={}; color={}'.format(
            namestr, is_accepted, scenariocodes, color)
        full_out = S2nOutput(
            len(stdrecs), query_term, self.SERVICE_TYPE, lout.provider, 
            provider_query=queries, record_format=Lifemapper.RECORD_FORMAT_MAP, 
            records=stdrecs, errors=errmsgs)
        return full_out.response

    # ...............................................
    def get_records(
            self, namestr, req_providers, is_accepted, scenariocodes, color):
        allrecs = []
        # for response metadata
        common_query = ''
        if namestr is not None:
            common_query = 'namestr={}'.format(namestr)
            
        provnames = []
        for pr in req_providers:
            # Lifemapper
            if pr == ServiceProvider.Lifemapper[S2nKey.PARAM]:
                lmoutput = self._get_lifemapper_records(
                    namestr, is_accepted, scenariocodes, color)
                allrecs.append(lmoutput)
                provnames.append(ServiceProvider.Lifemapper[S2nKey.NAME])
        # Assemble
        provstr = ','.join(provnames)
        full_out = S2nOutput(
            len(allrecs), common_query, self.SERVICE_TYPE, provstr, records=allrecs,
            record_format=S2n.RECORD_FORMAT)
        return full_out

    # ...............................................
    @cherrypy.tools.json_out()
    def GET(self, namestr=None, provider=None, gbif_parse=True, gbif_accepted=True, 
            scenariocode=None, color=None, **kwargs):
        """Get one or more taxon records for a scientific name string from each
        available name service.
        
        Args:
            namestr: a scientific name
            gbif_parse: flag to indicate whether to first use the GBIF parser 
                to parse a scientific name into canonical name 
        Return:
            a dictionary with keys for each service queried.  Values contain 
            lmtrex.services.api.v1.S2nOutput object with records as a 
            list of dictionaries of Lifemapper records corresponding to 
            maps with URLs and their layers in the Lifemapper archive
        """
        # No filter_params defined for Map service yet
        try:
            usr_params = self._standardize_params(
                namestr=namestr, provider=provider, gbif_parse=gbif_parse, 
                gbif_accepted=gbif_accepted, scenariocode=scenariocode, color=color)
        except Exception as e:
            traceback = get_traceback()
            output = self.get_failure(query_term=namestr, errors=[traceback])
        else:            
            # Who to query
            valid_providers = self.get_providers()
            valid_req_providers, invalid_providers = self.get_valid_requested_providers(
                usr_params['provider'], valid_providers)

            # What to query
            scencodes = usr_params['scenariocode']
            namestr = usr_params['namestr']
            try:
                if namestr is None:
                    output = self._show_online(providers=valid_providers)
                else:
                    # Query
                    output = self.get_records(
                        namestr, valid_req_providers, usr_params['is_accepted'], 
                        scencodes, usr_params['color'])
                    if invalid_providers:
                        msg = 'Invalid providers requested: {}'.format(
                            ','.join(invalid_providers))
                        output.append_value(S2nKey.ERRORS, msg)
            except Exception as e:
                output = self.get_failure(query_term=namestr, errors=[str(e)])
        return output.response


# .............................................................................
if __name__ == '__main__':
    # test    
    names = TST_VALUES.NAMES[5:9]
    names = ['Tulipa sylvestris']
    names = ['Phlox longifolia Nutt']
    svc = MapSvc()
    for namestr in names:
        for scodes in (None, 'worldclim-curr'):
            for prov in svc.get_providers():
                out = svc.GET(namestr=namestr, scenariocode=scodes, provider=prov)
                print_s2n_output(out, do_print_rec=True)
