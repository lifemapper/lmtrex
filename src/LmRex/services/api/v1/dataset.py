import cherrypy

from LmRex.common.lmconstants import (ServiceProvider, ServiceProviderNew, APIService)
from LmRex.tools.provider.gbif import GbifAPI
from LmRex.tools.provider.bison import BisonAPI
from LmRex.tools.utils import get_traceback

from LmRex.services.api.v1.base import _S2nService
from LmRex.services.api.v1.s2n_type import (S2nOutput, S2nKey, print_s2n_output)
        
# .............................................................................
@cherrypy.expose
class DatasetSvc(_S2nService):
    SERVICE_TYPE = APIService.Dataset
    
    # ...............................................
    @classmethod
    def _get_providers(cls):
        provnames = set()
        for p in ServiceProviderNew.all():
            if APIService.Dataset in p[S2nKey.SERVICES]:
                provnames.add(p[S2nKey.PARAM])
        return provnames

    # ...............................................
    @classmethod
    def _get_gbif_records(cls, dataset_key, count_only):
        try:
            output = GbifAPI.get_occurrences_by_dataset(
                dataset_key, count_only)
        except Exception as e:
            traceback = get_traceback()
            output = cls.get_failure(query_term=dataset_key, errors=[traceback])
        return output

    # ...............................................
    def get_records(self, dataset_key, providers, count_only):
        allrecs = []
        for pr in providers:
            # GBIF
            if pr == ServiceProviderNew.GBIF[S2nKey.PARAM]:
                gbif_output = self._get_gbif_records(dataset_key, count_only)
                allrecs.append(gbif_output)
        # Assemble
        if len(providers) > 1:
            provstr = ', '.join(providers)
            full_out = S2nOutput(
                len(allrecs), dataset_key, APIService.Dataset, provstr, 
                records=allrecs)
        else:
            full_out = allrecs[0]        
        return full_out

    # ...............................................
    @cherrypy.tools.json_out()
    def GET(self, dataset_key=None, provider=None, count_only=False, **kwargs):
        """Get one or more occurrence records for a dataset identifier from the
        GBIF occurrence service.
        
        Args:
            dataset_key: (optional) a unique dataset identifier for a collection of 
                occurrence records. If the identifier is not present, response will 
                contain the service status.
            provider: (optional) string containing a comma delimited list of provider 
                codes indicating which providers to query.  If the string is not present
                or 'all', all providers of this service will be queried.
            count_only: (optional) flag to indicate whether to return only a count, or 
                a count and records
            kwargs: any additional keyword arguments are ignored

        Return:
            LmRex.services.api.v1.S2nOutput object with optional records as a 
            list of dictionaries of GBIF records corresponding to specimen 
            occurrences in the GBIF database
                
        Note: 
            If count_only=False, the records element will contain a subset of 
            records available for that dataset.  The number of records will be
            less than or equal to the paging limit set by the provider.  
        Note: 
            The dataset_key is an identifier assigned by GBIF to collections
            which publish their datasets to GBIF.
        """

        try:
            usr_params = self._standardize_params(
                dataset_key=dataset_key, provider=provider, count_only=count_only)
            dataset_key = usr_params['dataset_key']
            # Who to query
            req_providers = self.get_valid_requested_providers(usr_params['provider'])
            # What to query
            if not dataset_key:
                output = self._show_online(providers=req_providers)
            else:
                output = self.get_records(
                    dataset_key, req_providers, usr_params['count_only'])
                
        except Exception as e:
            traceback = get_traceback()
            output = self.get_failure(query_term=dataset_key, errors=[traceback])
        return output.response
    
# # .............................................................................
# @cherrypy.expose
# class _DatasetSvc(_S2nService):
#     SERVICE_TYPE = APIService.Dataset

#  .............................................................................
# @cherrypy.expose
# class DatasetGBIF(_DatasetSvc):
#     PROVIDER = ServiceProvider.GBIF
#      ...............................................
#     def get_records(self, dataset_key, count_only):
#          'do_limit' limits the number of records returned to the GBIF limit
#         output = GbifAPI.get_occurrences_by_dataset(
#             dataset_key, count_only)
#         return output
# 
#      ...............................................
#     @cherrypy.tools.json_out()
#     def GET(self, dataset_key=None, provider=None, count_only=False, **kwargs):
#         """Get one or more occurrence records for a dataset identifier from the
#         GBIF occurrence service.
#         
#         Args:
#             dataset_key: a unique dataset identifier for a collection of 
#                 occurrence records.
#             provider: provider code to indicate who to query
#             count_only: flag to indicate whether to return only a count, or 
#                 a count and records
#             kwargs: any additional keyword arguments are ignored
# 
#         Return:
#             LmRex.services.api.v1.S2nOutput object with optional records as a 
#             list of dictionaries of GBIF records corresponding to specimen 
#             occurrences in the GBIF database
#                 
#         Note: 
#             If count_only=False, the records element will contain a subset of 
#             records available for that dataset.  The number of records will be
#             less than or equal to the paging limit set by the provider.  
#         Note: 
#             The dataset_key is an identifier assigned by GBIF to collections
#             which publish their datasets to GBIF.
#         """
#         try:
#             usr_params = self._standardize_params(
#                 dataset_key=dataset_key, count_only=count_only)
#             dataset_key = usr_params['dataset_key']
#             if not dataset_key:
#                 output = self._show_online()
#             else:
#                 output = self.get_records(dataset_key, usr_params['count_only'])
#         except Exception as e:
#             traceback = get_traceback()
#             output = self.get_failure(query_term=dataset_key, errors=[traceback])
#         return output.response

# # .............................................................................
# @cherrypy.expose
# class DatasetTentacles(_DatasetSvc):
#     PROVIDER = ServiceProvider.S2N
#     # ...............................................
#     def _get_records(self, dsid, count_only):
#         allrecs = []
#         
#         # GBIF copy/s of Specify Record
#         dg = DatasetGBIF()
#         gbif_output = dg.GET(dataset_key=dsid, count_only=count_only)
#         allrecs.append(gbif_output.response)
# 
#         full_out = S2nOutput(
#             len(allrecs), dsid, APIService.Dataset, self.PROVIDER, 
#             records=allrecs)        
#         return full_out
# 
#     # ...............................................
#     # ...............................................
#     @cherrypy.tools.json_out()
#     def GET(self, dataset_key=None, count_only=False, **kwargs):
#         """Get one or more occurrence records for a dataset identifier from all
#         available occurrence record services.
#         
#         Args:S2
#             dataset_key: a unique dataset identifier for a collection of 
#                 occurrence records.
#             count_only: flag to indicate whether to return only a count, or 
#                 a count and records
#             kwargs: any additional keyword arguments are ignored
# 
#         Return:
#             a dictionary with keys for each service queried.  Service values 
#             LmRex.services.api.v1.S2nOutput object with optional records as a 
#             list of dictionaries of GBIF records corresponding to specimen 
#             occurrences in the GBIF database
#               
#         Note: 
#             If count_only=False, the records element will contain a subset of 
#             records available for that dataset.  The number of records will be
#             less than or equal to the paging limit set by the provider.  
#         Note: 
#             The dataset_key is an identifier assigned by GBIF to collections
#             which publish their datasets to GBIF.  BISON maintains this value 
#             in records they retrieve from GBIF. 
#         """
#         try:
#             usr_params = self._standardize_params(
#                 dataset_key=dataset_key, count_only=count_only)
#             output = self._get_records(
#                 usr_params['dataset_key'], usr_params['count_only'])
#         except Exception as e:
#             output = self.get_failure(errors=[str(e)])
#         return output.response
    
# .............................................................................
if __name__ == '__main__':
    # test
    from LmRex.common.lmconstants import TST_VALUES
    
    svc = DatasetSvc()
    for count_only in [True, False]:
        out = svc.GET(
            dataset_key=TST_VALUES.DS_GUIDS_W_SPECIFY_ACCESS_RECS[0], 
            provider='gbif',
            count_only=count_only)
        print_s2n_output(out)
            

"""
http://notyeti-192.lifemapper.org/api/v1/dataset/gbif/56caf05f-1364-4f24-85f6-0c82520c2792?count_only=false
"""