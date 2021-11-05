import cherrypy
from http import HTTPStatus

from lmtrex.common.lmconstants import (APIService, ServiceProvider)
from lmtrex.common.s2n_type import (S2nKey, S2nOutput, S2nSchema, print_s2n_output)
from lmtrex.services.api.v1.base import _S2nService
from lmtrex.tools.provider.specify_resolver import SpecifyResolverAPI
from lmtrex.tools.utils import get_traceback

collection = 'spcoco'
solr_location = 'notyeti-192.lifemapper.org'

# .............................................................................
@cherrypy.expose
@cherrypy.popargs('occid')
class ResolveSvc(_S2nService):
    """Query the Specify Resolver with a UUID for a resolvable GUID and URL"""
    SERVICE_TYPE = APIService.Resolve
    ORDERED_FIELDNAMES = S2nSchema.get_s2n_fields(APIService.Resolve['endpoint'])

    # ...............................................
    @staticmethod
    def get_url_from_meta(std_output):
        url = msg = None
        try:
            solr_doc = std_output[S2nKey.RECORDS][0]
        except:
            pass
        else:
            # Get url from ARK for Specify query
            try:
                url = solr_doc['url']
            except Exception as e:
                pass
            else:
                if not url.startswith('http'):
                    msg = ('No direct record access to {}'.format(url))
                    url = None
        return (url, msg)
    
    # ...............................................
    def resolve_specify_guid(self, occid):
        try:
            output = SpecifyResolverAPI.query_for_guid(occid)
            output.format_records(self.ORDERED_FIELDNAMES)
        except Exception as e:
            traceback = get_traceback()
            output = SpecifyResolverAPI.get_api_failure(
                self.SERVICE_TYPE['endpoint'], HTTPStatus.INTERNAL_SERVER_ERROR, 
                errinfo={'error': [traceback]})
        return output.response

    # ...............................................
    def count_resolvable_specify_recs(self):
        std_output = SpecifyResolverAPI.count_docs()
        return std_output
    
    # ...............................................
    def get_counts(self, req_providers):
        allrecs = []
        # for response metadata
        provnames = []
        for pr in req_providers:
            # Address single record
            if pr == ServiceProvider.Specify[S2nKey.PARAM]:
                sp_output = self.count_resolvable_specify_recs()
                allrecs.append(sp_output)
                provnames.append(ServiceProvider.Specify[S2nKey.NAME])
        # Assemble
        provstr = ','.join(provnames)
        full_out = S2nOutput(
            len(allrecs), self.SERVICE_TYPE['endpoint'], provstr, records=allrecs,
            record_format=self.SERVICE_TYPE[S2nKey.RECORD_FORMAT])
        return full_out

    # ...............................................
    def get_records(self, occid, req_providers):
        allrecs = []
        # for response metadata
        provstr = ','.join(req_providers)
        query_term = 'occid={}&provider={}'.format(occid, provstr)
        for pr in req_providers:
            # Address single record
            if pr == ServiceProvider.Specify[S2nKey.PARAM]:
                sp_output = self.resolve_specify_guid(occid)
                allrecs.append(sp_output)
        # Assemble
        prov_meta = self._get_s2n_provider_response_elt(query_term=query_term)
        full_out = S2nOutput(
            len(allrecs), self.SERVICE_TYPE['endpoint'], provider=prov_meta, 
            records=allrecs, errors={})
        return full_out

        
    # ...............................................
    @cherrypy.tools.json_out()
    def GET(self, occid=None, provider=None, **kwargs):
        """Get zero or one record for an identifier from the resolution
        service du jour (DOI, ARK, etc) or get a count of all records indexed
        by this resolution service.
        
        Args:
            occid: an occurrenceID, a DarwinCore field intended for a globally 
                unique identifier (https://dwc.tdwg.org/list/#dwc_occurrenceID)
            provider: comma-delimited list of requested provider codes.  Codes are delimited
                for each in lmtrex.common.lmconstants ServiceProvider
            kwargs: any additional keyword arguments are ignored

        Return:
            A dictionary of metadata and a count of records found in GBIF and 
            an optional list of records.
                
        Note: 
            There will never be more than one record returned.
        """
        error_description = None
        http_status = int(HTTPStatus.OK)

        valid_providers = self.get_valid_providers()
        if occid is None:
            output = self._show_online(valid_providers)
        elif occid.lower() == 'count':
            output = self.count_resolvable_specify_recs()
        else:   
            try:
                good_params, _, errinfo = self._standardize_params(
                    occid=occid, provider=provider)
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
                        output = self.get_records(good_params['occid'], good_params['provider'])
    
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
    # test
    from lmtrex.common.lmconstants import TST_VALUES
    
    params = [None, TST_VALUES.GUIDS_W_SPECIFY_ACCESS[0]]
    for occid in params:
        print(occid)
        # Specify ARK Record
        svc = ResolveSvc()
        std_output = svc.GET(occid)
        print_s2n_output(std_output, do_print_rec=True)
