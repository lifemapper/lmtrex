import cherrypy

from lmtrex.common.lmconstants import (ServiceProvider, APIService)

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
# @cherrypy.popargs('path_occ_id')
class OccurrenceSvc(_S2nService):
    SERVICE_TYPE = APIService.Occurrence

    # ...............................................
    @classmethod
    def get_providers(cls, filter_params=None):
        provnames = set()
        if filter_params is None:
            for p in ServiceProvider.all():
                if cls.SERVICE_TYPE in p[S2nKey.SERVICES]:
                    provnames.add(p[S2nKey.PARAM])
        # Fewer providers by dataset
        elif 'dataset_key' in filter_params.keys():
            provnames = set([ServiceProvider.GBIF[S2nKey.PARAM]])
        return provnames

    # ...............................................
    def _get_specify_records(self, occid, count_only):
        # Resolve for record URL
        spark = ResolveSvc()
        std_output = spark.get_specify_records(occid)
        (url, msg) = spark.get_url_from_meta(std_output)
                
        try:
            output = SpecifyPortalAPI.get_specify_record(occid, url, count_only)
        except Exception as e:
            traceback = get_traceback()
            output = self.get_failure(
                provider=ServiceProvider.Specify[S2nKey.NAME], query_term=occid, 
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
                provider=ServiceProvider.MorphoSource[S2nKey.NAME], query_term=occid, 
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
                query_term = 'occid={}; count_only={}'.format(occid, count_only)
                output = GbifAPI.get_occurrences_by_occid(
                    occid, count_only=count_only)
            elif dataset_key is not None:
                query_term = 'dataset_key={}; count_only={}'.format(dataset_key, count_only)
                output = GbifAPI.get_occurrences_by_dataset(
                    dataset_key, count_only)
        except Exception as e:
            traceback = get_traceback()
            output = self.get_failure(
                provider=ServiceProvider.GBIF[S2nKey.NAME], query_term=query_term, 
                errors=[traceback])
        return output.response

    # ...............................................
    def get_records(self, occid, req_providers, count_only, filter_params=None):
        allrecs = []
        # for response metadata
        query_term = ''
        dskey = None
        if occid is not None:
            query_term = 'occid={}; count_only={}'.format(occid, count_only)
        elif filter_params:
            try:
                dskey = filter_params['dataset_key']
                query_term = 'dataset_key={}; count_only={}'.format(dskey, count_only)
            except:
                query_term = 'invalid query term'
                
        provnames = []
        for pr in req_providers:
            # Address single record
            if occid is not None:
                # GBIF
                if pr == ServiceProvider.GBIF[S2nKey.PARAM]:
                    gbif_output = self._get_gbif_records(occid, dskey, count_only)
                    allrecs.append(gbif_output)
                    provnames.append(ServiceProvider.GBIF[S2nKey.NAME])
                # iDigBio
                elif pr == ServiceProvider.iDigBio[S2nKey.PARAM]:
                    idb_output = self._get_idb_records(occid, count_only)
                    allrecs.append(idb_output)
                    provnames.append(ServiceProvider.iDigBio[S2nKey.NAME])
                # MorphoSource
                elif pr == ServiceProvider.MorphoSource[S2nKey.PARAM]:
                    mopho_output = self._get_mopho_records(occid, count_only)
                    allrecs.append(mopho_output)
                    provnames.append(ServiceProvider.MorphoSource[S2nKey.NAME])
                # Specify
                elif pr == ServiceProvider.Specify[S2nKey.PARAM]:
                    sp_output = self._get_specify_records(occid, count_only)
                    allrecs.append(sp_output)
                    provnames.append(ServiceProvider.Specify[S2nKey.NAME])
            # Filter by parameters
            elif dskey:
                if pr == ServiceProvider.GBIF[S2nKey.PARAM]:
                    gbif_output = self._get_gbif_records(occid, dskey, count_only)
                    allrecs.append(gbif_output)
                    provnames.append(ServiceProvider.GBIF[S2nKey.NAME])

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
        filter_params = dskey = None
            
        try:
            usr_params = self._standardize_params(
                occid=occid, provider=provider, dataset_key=dataset_key, 
                count_only=count_only)
        except Exception as e:
            traceback = get_traceback()
            output = self.get_failure(query_term=occid, errors=[traceback])
        else:
            # Who to query
            valid_providers = self.get_providers(filter_params=filter_params)
            valid_req_providers, invalid_providers = self.get_valid_requested_providers(
                usr_params['provider'], valid_providers)

            # What to query: address one occurrence record, with optional filters
            occid = usr_params['occid']
            dskey = usr_params['dataset_key']
            try:
                if occid is None and dskey is None:
                    output = self._show_online(providers=valid_req_providers)
                else:
                    output = self.get_records(
                        occid, valid_req_providers, usr_params['count_only'], 
                        filter_params={'dataset_key': dskey})
                    if invalid_providers:
                        msg = 'Invalid providers requested: {}'.format(
                            ','.join(invalid_providers))
                        output.append_value(S2nKey.ERRORS, msg)
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
            for prov in svc.get_providers(filter_params={'dataset_key': dskey}):
                out = svc.GET(
                    occid=None, provider=prov, dataset_key=dskey, count_only=count_only)
                print_s2n_output(out)
