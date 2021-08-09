import cherrypy
from http import HTTPStatus

from lmtrex.common.lmconstants import (APIService, S2N_SCHEMA, ServiceProvider)
from lmtrex.services.api.v1.base import _S2nService
from lmtrex.services.api.v1.s2n_type import (S2nKey, S2nOutput, print_s2n_output)
from lmtrex.tools.provider.gbif import GbifAPI
from lmtrex.tools.provider.itis import ItisAPI
from lmtrex.tools.utils import get_traceback
from lmtrex.tools.provider.idigbio import IdigbioAPI

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
            output = GbifAPI.get_api_failure(
                self.SERVICE_TYPE['endpoint'], HTTPStatus.INTERNAL_SERVER_ERROR, 
                errinfo={'error': [traceback]})
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
            output = IdigbioAPI.get_api_failure(
                self.SERVICE_TYPE['endpoint'], HTTPStatus.INTERNAL_SERVER_ERROR, 
                errinfo={'error': [traceback]})
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
            query_term = 'namestr={}&provider={}&is_accepted={}&gbif_count={}&kingdom={}'.format(
                namestr, ','.join(req_providers), is_accepted, gbif_count, kingdom)
            
        for pr in req_providers:
            # Address single record
            if namestr is not None:
                # GBIF
                if pr == ServiceProvider.GBIF[S2nKey.PARAM]:
                    goutput = self._get_gbif_records(namestr, is_accepted, gbif_count)
                    allrecs.append(goutput)
                #  ITIS
                elif pr == ServiceProvider.ITISSolr[S2nKey.PARAM]:
                    isoutput = self._get_itis_records(namestr, is_accepted, kingdom)
                    allrecs.append(isoutput)
            # TODO: enable filter parameters
            
        # Assemble
        prov_meta = self._get_s2n_provider_response_elt(query_term=query_term)
        # TODO: Figure out why errors are retained from query to query!!!  Resetting to {} works.
        full_out = S2nOutput(
            len(allrecs), self.SERVICE_TYPE['endpoint'], provider=prov_meta, 
            records=allrecs, errors={})

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
        error_description = None
        http_status = int(HTTPStatus.OK)

        valid_providers = self.get_valid_providers()
        if namestr is None:
            output = self._show_online(valid_providers)
        else:
            # No filter_params defined for Name service yet
            try:
                good_params, errinfo = self._standardize_params(
                    namestr=namestr, provider=provider, is_accepted=is_accepted, 
                    gbif_parse=gbif_parse, gbif_count=gbif_count, kingdom=kingdom)
                # Bad parameters
                try:
                    error_description = '; '.join(errinfo['error'])                            
                    http_status = int(HTTPStatus.BAD_REQUEST)
                except:
                    pass
            except Exception as e:
                error_description = get_traceback()
                http_status = int(HTTPStatus.INTERNAL_SERVER_ERROR)

            else:
                if http_status != HTTPStatus.BAD_REQUEST:
                    try:
                        # Do Query!
                        output = self.get_records(
                            good_params['namestr'], good_params['provider'], good_params['is_accepted'], 
                            good_params['gbif_count'], good_params['kingdom'])
    
                        # Add message on invalid parameters to output
                        try:
                            for err in errinfo['warning']:
                                output.append_error('warning', err)
                        except:
                            pass
        
                    except Exception as e:
                        error_description = get_traceback()
                        http_status = int(HTTPStatus.INTERNAL_SERVER_ERROR)

        if http_status == HTTPStatus.OK:
            return output.response
        else:
            raise cherrypy.HTTPError(http_status, error_description)
            

# .............................................................................
if __name__ == '__main__':
    pass
    # test_names = TST_VALUES.NAMES[0:4]
    test_names = ['poa', 'Tulipa sylvestris']
    
    svc = NameSvc()
    # out = svc.GET()
    # print_s2n_output(out)
    # out = svc.GET(
    #     namestr='Tulipa sylvestris', is_accepted=False, gbif_parse=True, 
    #     gbif_count=True, kingdom=None)
    # print_s2n_output(out)
    out = svc.GET(
        namestr='Tulipa sylvestris', provider='gbifx', is_accepted=False, gbif_parse=True, 
        gbif_count=True, kingdom=None)
    print_s2n_output(out)
    for namestr in test_names:
        for prov in svc.get_providers():
            out = svc.GET(
                namestr=namestr, provider=prov, is_accepted=False, gbif_parse=True, 
                gbif_count=True, kingdom=None)
            print_s2n_output(out)
    print_s2n_output(out)
                
"""
"""