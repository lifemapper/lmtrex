import aiohttp
import asyncio
import cherrypy
from http import HTTPStatus

from lmtrex.common.lmconstants import (APIService, ServiceProvider)
from lmtrex.common.s2n_type import (S2nKey, S2nOutput, S2nSchema, print_s2n_output)

from lmtrex.services.api.v1.base import _S2nService

from lmtrex.tools.provider.gbif import GbifAPI
from lmtrex.tools.provider.ipni import IpniAPI
from lmtrex.tools.provider.itis import ItisAPI
from lmtrex.tools.provider.worms import WormsAPI
from lmtrex.tools.utils import get_traceback

# .............................................................................
@cherrypy.expose
@cherrypy.popargs('namestr')
class NameSvc(_S2nService):
    SERVICE_TYPE = APIService.Name
    ORDERED_FIELDNAMES = S2nSchema.get_s2n_fields(APIService.Name['endpoint'])
    
    # ...............................................
    def _get_gbif_records(self, session, namestr, is_accepted, gbif_count):
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
                keyfld = S2nSchema.get_gbif_taxonkey_fld()
                cntfld = S2nSchema.get_gbif_occcount_fld()
                urlfld = S2nSchema.get_gbif_occurl_fld()
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
                output.format_records(self.ORDERED_FIELDNAMES)
        return output.response

    # ...............................................
    def _get_ipni_records(self, session, namestr, is_accepted):
        try:
            output = IpniAPI.match_name(namestr, is_accepted=is_accepted)
        except Exception as e:
            traceback = get_traceback()
            output = IpniAPI.get_api_failure(
                self.SERVICE_TYPE['endpoint'], HTTPStatus.INTERNAL_SERVER_ERROR, 
                errinfo={'error': [traceback]})
        else:
            output.set_value(S2nKey.RECORD_FORMAT, self.SERVICE_TYPE[S2nKey.RECORD_FORMAT])
            output.format_records(self.ORDERED_FIELDNAMES)
        return output.response

    # ...............................................
    def _get_itis_records(self, session, namestr, is_accepted, kingdom):
        try:
            output = ItisAPI.match_name(namestr, is_accepted=is_accepted, kingdom=kingdom)
        except Exception as e:
            traceback = get_traceback()
            output = ItisAPI.get_api_failure(
                self.SERVICE_TYPE['endpoint'], HTTPStatus.INTERNAL_SERVER_ERROR, 
                errinfo={'error': [traceback]})
        else:
            output.set_value(S2nKey.RECORD_FORMAT, self.SERVICE_TYPE[S2nKey.RECORD_FORMAT])
            output.format_records(self.ORDERED_FIELDNAMES)
        return output.response

    # ...............................................
    def _get_worms_records(self, session, namestr, is_accepted):
        try:
            output = WormsAPI.match_name(namestr, is_accepted=is_accepted)
        except Exception as e:
            traceback = get_traceback()
            output = WormsAPI.get_api_failure(
                self.SERVICE_TYPE['endpoint'], HTTPStatus.INTERNAL_SERVER_ERROR, 
                errinfo={'error': [traceback]})
        else:
            output.set_value(S2nKey.RECORD_FORMAT, self.SERVICE_TYPE[S2nKey.RECORD_FORMAT])
            output.format_records(self.ORDERED_FIELDNAMES)
        return output.response

    # ...............................................
    async def get_records(
            self, namestr, req_providers, is_accepted, gbif_count, kingdom):
        allrecs = []
        # for response metadata
        query_term = ''
        if namestr is not None:
            query_term = 'namestr={}&provider={}&is_accepted={}&gbif_count={}&kingdom={}'.format(
                namestr, ','.join(req_providers), is_accepted, gbif_count, kingdom)
        
        async with aiohttp.ClientSession() as session:
            for pr in req_providers:
                # Address single record
                if namestr is not None:
                    # GBIF
                    if pr == ServiceProvider.GBIF[S2nKey.PARAM]:
                        goutput = self._get_gbif_records(session, namestr, is_accepted, gbif_count)
                        allrecs.append(goutput)
                    # IPNI
                    elif pr == ServiceProvider.IPNI[S2nKey.PARAM]:
                        isoutput = self._get_ipni_records(session, namestr, is_accepted)
                        allrecs.append(isoutput)
                    #  ITIS
                    elif pr == ServiceProvider.ITISSolr[S2nKey.PARAM]:
                        isoutput = self._get_itis_records(session, namestr, is_accepted, kingdom)
                        allrecs.append(isoutput)
                    #  WoRMS
                    elif pr == ServiceProvider.WoRMS[S2nKey.PARAM]:
                        woutput = self._get_worms_records(session, namestr, is_accepted)
                        allrecs.append(woutput)
            # TODO: enable filter parameters
            
        # Assemble
        prov_meta = self._get_s2n_provider_response_elt(query_term=query_term)
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
    test_names = [
        'Plagiloecia patina Lamarck, 1816', 
        'Poa annua',
        # 'Gnatholepis cauerensis (Bleeker, 1853)', 
        # 'Tulipa sylvestris']
    ]
    
    svc = NameSvc()
    for namestr in test_names:
        out = svc.GET(
            namestr=namestr, provider=None, is_accepted=False, gbif_parse=True, 
            gbif_count=True, kingdom=None)
        print_s2n_output(out, do_print_rec=True)
                
"""
"""