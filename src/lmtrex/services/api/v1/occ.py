import cherrypy

from lmtrex.common.lmconstants import (ServiceProviderNew, APIService)

from lmtrex.tools.provider.gbif import GbifAPI
from lmtrex.tools.provider.idigbio import IdigbioAPI
from lmtrex.tools.provider.mopho import MorphoSourceAPI
from lmtrex.tools.provider.specify import SpecifyPortalAPI
from lmtrex.tools.utils import get_traceback

from lmtrex.services.api.v1.base import _S2nService
from lmtrex.services.api.v1.resolve import ResolveSvc
from lmtrex.services.api.v1.s2n_type import (S2nOutput, S2nKey, S2n, print_s2n_output)

# .............................................................................
@cherrypy.expose
class OccurrenceSvc(_S2nService):
    SERVICE_TYPE = APIService.Occurrence

    # ...............................................
    @classmethod
    def get_providers(cls, search_params=None):
        provnames = set()
        if search_params is None:
            for p in ServiceProviderNew.all():
                if cls.SERVICE_TYPE in p[S2nKey.SERVICES]:
                    provnames.add(p[S2nKey.PARAM])
        # Fewer providers by dataset
        elif 'dataset_key' in search_params.keys():
            provnames = set([ServiceProviderNew.GBIF[S2nKey.PARAM]])
        return provnames

    # ...............................................
    def _get_specify_records(self, occid, count_only):
        # Resolve for record URL
        spark = ResolveSvc()
        std_output = spark.get_specify_records(occid)
        (url, msg) = spark.get_url_from_meta(std_output)
                
        if url is None:
            msgs = []
            if msg is not None:
                msgs.append(msg)
            msgs.append('No endpoint for Specify record with occurrenceID {}'.format(occid))
            output = self.get_failure(
                provider=ServiceProviderNew.Specify[S2nKey.NAME], query_term=occid, 
                errors=msgs)
        else:
            try:
                output = SpecifyPortalAPI.get_specify_record(occid, url, count_only)
            except Exception as e:
                traceback = get_traceback()
                output = self.get_failure(
                    provider=ServiceProviderNew.Specify[S2nKey.NAME], query_term=occid, 
                    errors=[traceback])
        return output.response

    # ...............................................
    def _get_mopho_records(self, occid, count_only):
        try:
            output = MorphoSourceAPI.get_occurrences_by_occid_page1(
                occid, count_only=count_only)
        except Exception as e:
            traceback = get_traceback()
            output = self.get_failure(
                provider=ServiceProviderNew.MorphoSource[S2nKey.NAME], query_term=occid, 
                errors=[traceback])
        return output.response

    # ...............................................
    def _get_idb_records(self, occid, count_only):
        try:
            output = IdigbioAPI.get_occurrences_by_occid(occid, count_only=count_only)
        except Exception as e:
            traceback = get_traceback()
            output = self.get_failure(query_term=occid, errors=[traceback])
        return output.response


    # ...............................................
    def _get_gbif_records(self, occid, dataset_key, count_only):
        try:
            if occid is not None:
                query_term = occid
                output = GbifAPI.get_occurrences_by_occid(
                    occid, count_only=count_only)
            elif dataset_key is not None:
                query_term = dataset_key
                output = GbifAPI.get_occurrences_by_dataset(
                    dataset_key, count_only)
        except Exception as e:
            traceback = get_traceback()
            output = self.get_failure(
                provider=ServiceProviderNew.GBIF[S2nKey.NAME], query_term=query_term, 
                errors=[traceback])
        return output.response

    # ...............................................
    def get_records(self, occid, req_providers, count_only, search_params=None):
        allrecs = []
        # for response metadata
        query_term = ''
        dskey = None
        if occid is not None:
            query_term = occid
        elif search_params:
            try:
                dskey = search_params['dataset_key']
                query_term = '{}'.format(search_params)
            except:
                query_term = 'invalid query term'
                
        provnames = []
        for pr in req_providers:
            # Address single record
            if occid is not None:
                # GBIF
                if pr == ServiceProviderNew.GBIF[S2nKey.PARAM]:
                    gbif_output = self._get_gbif_records(occid, dskey, count_only)
                    allrecs.append(gbif_output)
                    provnames.append(ServiceProviderNew.GBIF[S2nKey.NAME])
                # iDigBio
                elif pr == ServiceProviderNew.iDigBio[S2nKey.PARAM]:
                    idb_output = self._get_idb_records(occid, count_only)
                    allrecs.append(idb_output)
                    provnames.append(ServiceProviderNew.iDigBio[S2nKey.NAME])
                # MorphoSource
                elif pr == ServiceProviderNew.MorphoSource[S2nKey.PARAM]:
                    mopho_output = self._get_mopho_records(occid, count_only)
                    allrecs.append(mopho_output)
                    provnames.append(ServiceProviderNew.MorphoSource[S2nKey.NAME])
                # Specify
                elif pr == ServiceProviderNew.Specify[S2nKey.PARAM]:
                    sp_output = self._get_specify_records(occid, count_only)
                    allrecs.append(sp_output)
                    provnames.append(ServiceProviderNew.Specify[S2nKey.NAME])
            # Filter by parameters
            elif search_params:
                if dskey:
                    if pr == ServiceProviderNew.GBIF[S2nKey.PARAM]:
                        gbif_output = self._get_gbif_records(occid, dskey, count_only)
                        allrecs.append(gbif_output)
                        provnames.append(ServiceProviderNew.GBIF[S2nKey.NAME])

        # Assemble
        provstr = ','.join(provnames)
        full_out = S2nOutput(
            len(allrecs), query_term, self.SERVICE_TYPE, provstr, records=allrecs,
            record_format=S2n.RECORD_FORMAT)
        return full_out

    # ...............................................
    # ...............................................
    @cherrypy.tools.json_out()
    def GET(self, occid=None, provider=None, dataset_key=None, count_only=False, **kwargs):
        """Get one or more occurrence records for a dwc:occurrenceID from each
        available occurrence record service.
        
        Args:
            occid: an occurrenceID, a DarwinCore field intended for a globally 
                unique identifier (https://dwc.tdwg.org/list/#dwc_occurrenceID)
            count_only: flag to indicate whether to return only a count, or 
                a count and records
            kwargs: any additional keyword arguments are ignored

        Return:
            a dictionary with keys for each service queried.  Values contain 
            lmtrex.services.api.v1.S2nOutput object with optional records as a 
            list of dictionaries of records corresponding to specimen 
            occurrences in the provider database
        """
        search_params = None
        try:
            usr_params = self._standardize_params(
                occid=occid, provider=provider, dataset_key=dataset_key, 
                count_only=count_only)
            
            # What to query: address one occurrence record, with optional filters
            occid = usr_params['occid']
            if occid is None:
                # What to query: query for many records with filters
                dskey = usr_params['dataset_key']
                if dskey:
                    search_params = {'dataset_key': dskey}
            
            # Who to query
            valid_providers = self.get_providers(search_params=search_params)
            req_providers = self.get_valid_requested_providers(
                usr_params['provider'], valid_providers)
            
            if occid is None and search_params is None:
                output = self._show_online()
            else:
                # What to query: common filters
                count_only = usr_params['count_only']
                # Query
                output = self.get_records(
                    occid, req_providers, count_only, search_params=search_params)
        except Exception as e:
            traceback = get_traceback()
            output = self.get_failure(query_term=occid, errors=[traceback])
        return output.response
    

# .............................................................................
if __name__ == '__main__':
    from lmtrex.common.lmconstants import TST_VALUES
    occids = [TST_VALUES.GUIDS_W_SPECIFY_ACCESS[0]]
    dskeys = [TST_VALUES.DS_GUIDS_W_SPECIFY_ACCESS_RECS[0]]
    svc = OccurrenceSvc()
    # Query by occurrenceid
    for occid in occids:
        for count_only in [False]:
            # Get one provider at a time
            for prov in svc.get_providers():
                out = svc.GET(
                    occid=occid, provider=prov, count_only=count_only)
                print_s2n_output(out)
    # Get all providers for last occid
    out = svc.GET(occid=occid, count_only=count_only)
    print_s2n_output(out)
    
    # Query by datasetid
    for dskey in dskeys:
        for count_only in [True]:
            for prov in svc.get_providers(search_params={'dataset_key': dskey}):
                out = svc.GET(
                    occid=None, provider=prov, dataset_key=dskey, count_only=count_only)
                print_s2n_output(out)
