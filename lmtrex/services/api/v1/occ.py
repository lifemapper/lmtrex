import cherrypy

from lmtrex.common.lmconstants import (APIService, ServiceProvider)

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
@cherrypy.popargs('occid')
class OccurrenceSvc(_S2nService):
    SERVICE_TYPE = APIService.Occurrence

    # ...............................................
    @classmethod
    def get_providers(cls, filter_params=None):
        provnames = set()
        if filter_params is None:
            for p in ServiceProvider.all():
                if cls.SERVICE_TYPE['endpoint'] in p[S2nKey.SERVICES]:
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
                # elif pr == ServiceProvider.Specify[S2nKey.PARAM]:
                #     sp_output = self._get_specify_records(occid, count_only)
                #     allrecs.append(sp_output)
                #     provnames.append(ServiceProvider.Specify[S2nKey.NAME])
            # Filter by parameters
            elif dskey:
                if pr == ServiceProvider.GBIF[S2nKey.PARAM]:
                    gbif_output = self._get_gbif_records(occid, dskey, count_only)
                    allrecs.append(gbif_output)
                    provnames.append(ServiceProvider.GBIF[S2nKey.NAME])

        # Assemble
        provstr = ','.join(provnames)
        full_out = S2nOutput(
            len(allrecs), query_term, self.SERVICE_TYPE['endpoint'], provstr, records=allrecs,
            record_format=S2n.RECORD_FORMAT)
        return full_out

    # ...............................................
    def get_records_new(self, occid, req_providers, count_only, dataset_key=None):
        allrecs = []
        # for response metadata
        query_term = ''
        dskey = None
        if occid is not None:
            query_term = 'occid={}; count_only={}'.format(occid, count_only)
        elif dataset_key:
            try:
                query_term = 'dataset_key={}; count_only={}'.format(dataset_key, count_only)
            except:
                query_term = 'invalid query term'
                
        provnames = []
        for pr in req_providers:
            # Address single record
            if occid is not None:
                # GBIF
                if pr == ServiceProvider.GBIF[S2nKey.PARAM]:
                    gbif_output = self._get_gbif_records(occid, dataset_key, count_only)
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
            # Filter by parameters
            elif dskey:
                if pr == ServiceProvider.GBIF[S2nKey.PARAM]:
                    gbif_output = self._get_gbif_records(occid, dataset_key, count_only)
                    allrecs.append(gbif_output)
                    provnames.append(ServiceProvider.GBIF[S2nKey.NAME])

        # Assemble
        provstr = ','.join(provnames)
        full_out = S2nOutput(
            len(allrecs), query_term, self.SERVICE_TYPE['endpoint'], provstr, records=allrecs,
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
        valid_providers = self.get_valid_providers()
        if occid is None and dataset_key is None:
            output = self._show_online(valid_providers)
        elif occid.lower() in APIService.get_other_endpoints(self.SERVICE_TYPE):
            output = self._show_online(valid_providers)
        else:   
            # No filter_params defined for Name service yet
            try:
                good_params, info_valid_options = self._standardize_params_new(
                occid=occid, provider=provider, dataset_key=dataset_key, 
                count_only=count_only)
            except Exception as e:
                traceback = get_traceback()
                output = self.get_failure(query_term=occid, errors=[traceback])
            else:    
                # What to query
                try:
                    output = self.get_records_new(
                        good_params['occid'], good_params['provider'], good_params['count_only'], 
                        dataset_key=good_params['dataset_key'])

                    # Add message on invalid parameters to output
                    for key, options in info_valid_options.items():
                        msg = 'Valid {} options: {}'.format(key, ','.join(options))
                        output.append_value(S2nKey.ERRORS, msg)
                except Exception as e:
                    traceback = get_traceback()
                    output = self.get_failure(query_term=good_params['occid'], errors=[traceback])
        return output.response
    

# .............................................................................
if __name__ == '__main__':
    from lmtrex.common.lmconstants import TST_VALUES
    occids = TST_VALUES.GUIDS_WO_SPECIFY_ACCESS[0:3]
    
    dskeys = [TST_VALUES.DS_GUIDS_W_SPECIFY_ACCESS_RECS[0]]
    svc = OccurrenceSvc()
    occids.insert(0, None)
    # Get all providers
    for occid in occids:
        out = svc.GET(occid=occid, count_only=False)
        outputs = out['records']
        print_s2n_output(out)
        # for pout in outputs:
        #     if pout['count'] > 0:
        #         if pout['provider'] == 'Specify':
        #             specify_occ = pout['records'][0]
        #         elif pout['provider'] == 'GBIF':
        #             gbif_occ = pout['records'][0]
        #         elif pout['provider'] == 'iDigBio':
        #             idig_occ = pout['records'][0]
        #         elif pout['provider'] == 'MorphoSource':
        #             mopho_occ = pout['records'][0]
     
#     # Query by datasetid
#     for dskey in dskeys:
#         for count_only in [True]:
#             for prov in svc.get_providers(filter_params={'dataset_key': dskey}):
#                 out = svc.GET(
#                     occid=None, provider=prov, dataset_key=dskey, count_only=count_only)
#                 print_s2n_output(out)

    x = 1
    
"""
https://broker.spcoco.org/api/v1/occ/ed8cfa5a-7b47-11e4-8ef3-782bcb9cd5b5
https://broker-dev.spcoco.org/api/v1/occ/ed8cfa5a-7b47-11e4-8ef3-782bcb9cd5b5

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

from lmtrex.services.api.v1.occ import *

from lmtrex.common.lmconstants import TST_VALUES

occids = [TST_VALUES.GUIDS_W_SPECIFY_ACCESS[0]]
svc = OccurrenceSvc()

# Get all providers 
# Specify success
occid = occids[-1]

# Morphosource success
occid = TST_VALUES.GUIDS_WO_SPECIFY_ACCESS[0]

out = svc.GET(occid=occid, count_only=False)

specify_occ = gbif_occ = idig_occ = mopho_occ = None 
outputs = out['records']
for pout in outputs:
    if pout['count'] > 0:
        if pout['provider'] == 'Specify':
            specify_occ = pout['records'][0]
        elif pout['provider'] == 'GBIF':
            gbif_occ = pout['records'][0]
        elif pout['provider'] == 'iDigBio':
            idig_occ = pout['records'][0]
        elif pout['provider'] == 'MorphoSource':
            mopho_occ = pout['records'][0]


"""
