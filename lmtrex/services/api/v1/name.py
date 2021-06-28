import cherrypy
from http import HTTPStatus

from lmtrex.common.lmconstants import (
    APIService, S2N_SCHEMA, ServiceProvider, TST_VALUES)
from lmtrex.services.api.v1.base import _S2nService
from lmtrex.services.api.v1.s2n_type import (S2nKey, S2n, S2nOutput, print_s2n_output)
from lmtrex.tools.provider.gbif import GbifAPI
from lmtrex.tools.provider.itis import ItisAPI
from lmtrex.tools.utils import get_traceback

# .............................................................................
@cherrypy.expose
@cherrypy.popargs('namestr')
class NameSvc(_S2nService):
    SERVICE_TYPE = APIService.Name
    
    # ...............................................
    def _get_gbif_records(self, namestr, is_accepted, gbif_count):
        try:
            output = GbifAPI.match_name(namestr, is_accepted=is_accepted)
        except Exception as e:
            traceback = get_traceback()
            query_term = 'namestr={}&is_accepted={}'.format(namestr, is_accepted)
            output = self.get_failure(
                provider=ServiceProvider.GBIF[S2nKey.NAME], query_term=query_term, 
                errors=[{'error': traceback}])
        else:
            output.set_value(S2nKey.RECORD_FORMAT, self.SERVICE_TYPE[S2nKey.RECORD_FORMAT])

            # Add occurrence count to name records
            if gbif_count is True:
                prov_query_list = output.provider_query
                keyfld = S2N_SCHEMA.get_gbif_taxonkey_fld()
                cntfld = S2N_SCHEMA.get_gbif_occcount_fld()
                urlfld = S2N_SCHEMA.get_gbif_occurl_fld()
                for namerec in output.records:
                    try:
                        taxon_key = namerec[keyfld]
                    except Exception as e:
                        print('No usageKey for counting {} records'.format(namestr))
                    else:
                        # Add more info to each record
                        try:
                            count_output = GbifAPI.count_occurrences_for_taxon(taxon_key)
                        except Exception as e:
                            traceback = get_traceback()
                            print(traceback)
                        else:
                            try:
                                count_query = count_output.provider[S2nKey.PROVIDER_QUERY_URL][0]
                                namerec[cntfld] = count_output.count
                            except Exception as e:
                                traceback = get_traceback()
                                output.append_value(S2nKey.ERRORS, {'error': traceback})
                            else:
                                namerec[urlfld] = count_query
                                prov_query_list.append(count_query)
                # add count queries to list
                output.set_value(S2nKey.PROVIDER_QUERY_URL, prov_query_list)
        return output.response

    # ...............................................
    def _get_itis_records(self, namestr, is_accepted, kingdom):
        try:
            output = ItisAPI.match_name(
                namestr, is_accepted=is_accepted, kingdom=kingdom)
        except Exception as e:
            traceback = get_traceback()
            query_term = 'namestr={}&is_accepted={}&kingdom={}'.format(namestr, is_accepted, kingdom)
            output = self.get_failure(
                provider=ServiceProvider.iDigBio[S2nKey.NAME], query_term=query_term, 
                errors=[{'error': traceback}])
        else:
            output.set_value(S2nKey.RECORD_FORMAT, self.SERVICE_TYPE[S2nKey.RECORD_FORMAT])
        return output.response

    # ...............................................
    def get_records(
            self, namestr, req_providers, is_accepted, gbif_count, kingdom):
        allrecs = []
        # for response metadata
        query_term = ''
        if namestr is not None:
            query_term = 'namestr={}&provider={}'.format(namestr, ','.join(req_providers))
            
        provnames = []
        for pr in req_providers:
            # Address single record
            if namestr is not None:
                # GBIF
                if pr == ServiceProvider.GBIF[S2nKey.PARAM]:
                    goutput = self._get_gbif_records(namestr, is_accepted, gbif_count)
                    allrecs.append(goutput)
                    query_term = 'namestr={}&is_accepted={}&gbif_count={}'.format(
                        namestr, is_accepted, gbif_count)
                #  ITIS
                elif pr == ServiceProvider.ITISSolr[S2nKey.PARAM]:
                    isoutput = self._get_itis_records(namestr, is_accepted, kingdom)
                    allrecs.append(isoutput)
                    query_term = 'namestr={}&is_accepted={}&kingdom={}'.format(
                        namestr, is_accepted, kingdom)
            # TODO: enable filter parameters
            
        # Assemble
        prov_meta = self._get_s2n_provider_response_elt()
        full_out = S2nOutput(
            len(allrecs), query_term, self.SERVICE_TYPE['endpoint'], provider=prov_meta, 
            records=allrecs)

        return full_out

    # ...............................................
    @cherrypy.tools.json_out()
    def GET(self, namestr=None, provider=None, is_accepted=True, gbif_parse=True, 
            gbif_count=True, kingdom=None, **kwargs):
        """Get one or more taxon records for a scientific name string from each
        available name service.
        
        Args:
            namestr: a scientific name
            is_accepted: flag to indicate whether to limit to 'valid' or 
                'accepted' taxa in the ITIS or GBIF Backbone Taxonomy
            gbif_parse: flag to indicate whether to first use the GBIF parser 
                to parse a scientific name into canonical name
            gbif_count: flag to indicate whether to count GBIF occurrences of 
                this taxon
            kingdom: not yet implemented
            kwargs: any additional keyword arguments are ignored

        Return:
            a dictionary with keys for each service queried.  Values contain 
            lmtrex.services.api.v1.S2nOutput object with records as a list of 
            dictionaries of records corresponding to names in the provider 
            taxonomy.
        """
        valid_providers = self.get_valid_providers()
        if namestr is None:
            output = self._show_online(valid_providers)
        else:
            # No filter_params defined for Name service yet
            try:
                good_params, option_errors, is_fatal = self._standardize_params(
                    namestr=namestr, provider=provider, is_accepted=is_accepted, 
                    gbif_parse=gbif_parse, gbif_count=gbif_count, kingdom=kingdom)
            except Exception as e:
                traceback = get_traceback()
                query_term='namestr={}&provider={}&gbif_parse={}&is_accepted={}&gbif_count={}&kingdom={}'.format(
                    namestr, provider, gbif_parse, is_accepted, gbif_count, kingdom=kingdom)

                output = self.get_failure(query_term=namestr, errors=[{'error': traceback}])
            else:
                if is_fatal:
                    raise cherrypy.HTTPError(
                        HTTPStatus.BAD_REQUEST, 'Request includes one or more invalid parameters')
                else:
                    try:
                        # Do Query!
                        output = self.get_records(
                            good_params['namestr'], good_params['provider'], good_params['is_accepted'], 
                            good_params['gbif_count'], good_params['kingdom'])
    
                        # Add message on invalid parameters to output
                        for err in option_errors:
                            output.append_value(S2nKey.ERRORS, err)
        
                    except Exception as e:
                        query_term='namestr={}&provider={}&is_accepted={}&gbif_count={}&kingdom={}'.format(
                            good_params['namestr'], good_params['provider'], good_params['is_accepted'], 
                            good_params['gbif_count'], good_params['kingdom'])
                        output = self.get_failure(query_term=query_term, errors=[{'error': str(e)}])
        return output.response
            

# .............................................................................
if __name__ == '__main__':

    # test
    # test_names = TST_VALUES.NAMES[0:4]
    test_names = [None, 'poa', 'Tulipa sylvestris']
    
    
    svc = NameSvc()
    out = svc.GET()
    print_s2n_output(out)
    out = svc.GET(
        namestr='Tulipa sylvestris', is_accepted=False, gbif_parse=True, 
        gbif_count=True, kingdom=None)
    print_s2n_output(out)
    out = svc.GET(
        namestr='Tulipa sylvestris', provider='gbifx', is_accepted=False, gbif_parse=True, 
        gbif_count=True, kingdom=None)
    print_s2n_output(out)
    # for namestr in test_names:
    #     for prov in svc.get_providers():
    #         out = svc.GET(
    #             namestr=namestr, provider=prov, is_accepted=False, gbif_parse=True, 
    #             gbif_count=True, kingdom=None)
    #         print_s2n_output(out)
    # print_s2n_output(out)
                
"""
https://broker-dev.spcoco.org/api/v1/name/Poa annua?provider=gbif
https://broker-dev.spcoco.org/api/v1/name/occ/Plagioecia%20patina

import cherrypy
import json

from lmtrex.common.lmconstants import (
    ServiceProvider, APIService, TST_VALUES)
from lmtrex.services.api.v1.base import _S2nService
from lmtrex.services.api.v1.s2n_type import (S2nKey, S2nOutput, print_s2n_output)
from lmtrex.tools.provider.gbif import GbifAPI
from lmtrex.tools.provider.itis import ItisAPI
from lmtrex.tools.utils import get_traceback
from lmtrex.services.api.v1.name import NameSvc

ss = '41107:$Poa annua aquatica$Poa annua reptans$Aira pumila$Catabrosa pumila$Ochlopoa annua$Poa aestivalis$Poa algida$Poa annua annua$Poa annua eriolepis$Poa annua rigidiuscula$Poa annua reptans$'


namestr = TST_VALUES.NAMES[4]
svc = NameSvc()
gparse = True
prov = 'gbif'
out = svc.GET(namestr=namestr, provider=prov, is_accepted=False, gbif_parse=gparse,gbif_count=True, kingdom=None)
print_s2n_output(out)

"""