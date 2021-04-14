import cherrypy

from lmtrex.common.lmconstants import (
    ServiceProviderNew, APIService, TST_VALUES)
from lmtrex.services.api.v1.base import _S2nService
from lmtrex.services.api.v1.s2n_type import (S2nKey, S2nOutput, print_s2n_output)
from lmtrex.tools.provider.gbif import GbifAPI
from lmtrex.tools.provider.itis import ItisAPI
from lmtrex.tools.utils import get_traceback

# .............................................................................
@cherrypy.expose
class NameSvc(_S2nService):
    SERVICE_TYPE = APIService.Name
    
    # ...............................................
    @classmethod
    def get_providers(self, search_params=None):
        provnames = set()
        # Ignore as-yet undefined search_params
        for p in ServiceProviderNew.all():
            if APIService.Name in p[S2nKey.SERVICES]:
                provnames.add(p[S2nKey.PARAM])
        return provnames
    
    # ...............................................
    def _get_gbif_records(self, namestr, gbif_status, gbif_count):
        try:
            # Get name from Gbif        
            output = GbifAPI.match_name(namestr, status=gbif_status)
        except Exception as e:
            traceback = get_traceback()
            output = self.get_failure(
                provider=ServiceProviderNew.GBIF[S2nKey.NAME], query_term=namestr, 
                errors=[traceback])
        else:
            prov_query_list = output.provider_query
            # Add occurrence count to name records
            if gbif_count is True:
                for namerec in output.records:
                    try:
                        taxon_key = namerec['usageKey']
                    except Exception as e:
                        print('No usageKey for counting {} records'.format(namestr))
                    else:
                        # Add more info to each record
                        try:
                            outdict = GbifAPI.count_occurrences_for_taxon(taxon_key)
                        except Exception as e:
                            traceback = get_traceback()
                            print(traceback)
                        else:
                            namerec[S2nKey.OCCURRENCE_COUNT] = outdict[S2nKey.COUNT]
                            namerec[S2nKey.OCCURRENCE_URL] = outdict[S2nKey.OCCURRENCE_URL]
                            prov_query_list.extend(outdict[S2nKey.PROVIDER_QUERY])
     
                output.set_value(S2nKey.PROVIDER_QUERY, prov_query_list)
        return output.response

    # ...............................................
    def _get_itis_records(self, namestr, itis_accepted, kingdom):
        try:
            output = ItisAPI.match_name(
                namestr, itis_accepted=itis_accepted, kingdom=kingdom)
        except Exception as e:
            traceback = get_traceback()
            output = self.get_failure(
                provider=ServiceProviderNew.iDigBio[S2nKey.NAME], query_term=namestr, 
                errors=[traceback])
        return output.response

    # ...............................................
    def get_records(
            self, namestr, req_providers, gbif_status, gbif_count, itis_accepted, kingdom, 
            search_params=None):
        allrecs = []
        # for response metadata
        query_term = ''
        if namestr is not None:
            query_term = namestr
        elif search_params:
            query_term = 'invalid query term'
            
        provnames = []
        for pr in req_providers:
            # Address single record
            if namestr is not None:
                # GBIF
                if pr == ServiceProviderNew.GBIF[S2nKey.PARAM]:
                    goutput = self._get_gbif_records(namestr, gbif_status, gbif_count)
                    allrecs.append(goutput)
                    provnames.append(ServiceProviderNew.GBIF[S2nKey.NAME])
                #  ITIS
                elif pr == ServiceProviderNew.ITISSolr[S2nKey.PARAM]:
                    isoutput = self._get_itis_records(namestr, itis_accepted, kingdom)
                    allrecs.append(isoutput)
                    provnames.append(ServiceProviderNew.ITISSolr[S2nKey.NAME])
            # Filter by parameters
            # TODO: enable search parameters
            elif search_params:
                pass
            
        # Assemble
        provstr = ','.join(provnames)
        full_out = S2nOutput(
            len(allrecs), query_term, self.SERVICE_TYPE, provstr, records=allrecs)

        return full_out

    # ...............................................
    @cherrypy.tools.json_out()
    def GET(self, namestr=None, provider=None, gbif_accepted=True, gbif_parse=True, 
            gbif_count=True, itis_accepted=None, kingdom=None, **kwargs):
        """Get one or more taxon records for a scientific name string from each
        available name service.
        
        Args:
            namestr: a scientific name
            gbif_accepted: flag to indicate whether to limit to 'valid' or 
                'accepted' taxa in the GBIF Backbone Taxonomy
            gbif_parse: flag to indicate whether to first use the GBIF parser 
                to parse a scientific name into canonical name
            gbif_count: flag to indicate whether to count GBIF occurrences of 
                this taxon
            itis_accepted: flag to indicate whether to limit to 'valid' or 
                'accepted' taxa in the ITIS Taxonomy
            kingdom: not yet implemented
            kwargs: any additional keyword arguments are ignored

        Return:
            a dictionary with keys for each service queried.  Values contain 
            lmtrex.services.api.v1.S2nOutput object with records as a list of 
            dictionaries of records corresponding to names in the provider 
            taxonomy.
        """
        # No search_params defined for Name service yet
        search_params = None
        try:
            usr_params = self._standardize_params(
                namestr=namestr, provider=provider, gbif_accepted=gbif_accepted, 
                gbif_parse=gbif_parse, gbif_count=gbif_count, itis_accepted=itis_accepted, 
                kingdom=kingdom)
            
            # What to query
            namestr = usr_params['namestr']
            # Who to query
            valid_providers = self.get_providers(search_params=search_params)
            req_providers = self.get_valid_requested_providers(
                usr_params['provider'], valid_providers)

            if namestr is None and search_params is None:
                output = self._show_online(providers=valid_providers)
            else:
                # common filters
                gbif_status = usr_params['gbif_status']
                gbif_count = usr_params['gbif_count']
                itis_accepted = usr_params['itis_accepted'] 
                kingdom = usr_params['kingdom']
                # Query
                output = self.get_records(
                    namestr, req_providers, gbif_status, gbif_count, itis_accepted, 
                    kingdom, search_params=search_params)
                
        except Exception as e:
            output = self.get_failure(query_term=namestr, errors=[str(e)])
        
        return output.response
#         import json
#         s = json.dumps(output.response)
#         return s
            

# .............................................................................
if __name__ == '__main__':

    # test
    test_names = TST_VALUES.NAMES[0:4]
#     test_names.append(TST_VALUES.GUIDS_W_SPECIFY_ACCESS[0])
    
    svc = NameSvc()
    for namestr in test_names:
        for gparse in [True]:
            for prov in ['itis']:
#             for prov in svc.get_providers():
                out = svc.GET(
                    namestr=namestr, provider=prov, gbif_accepted=False, gbif_parse=gparse, 
                    gbif_count=True, itis_accepted=True, kingdom=None)
                print_s2n_output(out)
#     # Try once with all providers
#     out = svc.GET(
#         namestr=namestr, provider=None, gbif_accepted=False, gbif_parse=True, 
#         gbif_count=True, itis_accepted=True, kingdom=None)
#     print_s2n_output(out)
                
"""
import cherrypy
import json

from lmtrex.common.lmconstants import (
    ServiceProviderNew, APIService, TST_VALUES)
from lmtrex.services.api.v1.base import _S2nService
from lmtrex.services.api.v1.s2n_type import (S2nKey, S2nOutput, print_s2n_output)
from lmtrex.tools.provider.gbif import GbifAPI
from lmtrex.tools.provider.itis import ItisAPI
from lmtrex.tools.utils import get_traceback
from lmtrex.services.api.v1.name import NameSvc


namestr = TST_VALUES.NAMES[4]
svc = NameSvc()
gparse = True
prov = 'gbif'
out = svc.GET(namestr=namestr, provider=prov, gbif_accepted=False, gbif_parse=gparse,gbif_count=True, itis_accepted=True, kingdom=None)
print_s2n_output(out)

"""