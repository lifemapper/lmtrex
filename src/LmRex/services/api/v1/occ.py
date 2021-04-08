import cherrypy

from LmRex.common.lmconstants import (ServiceProviderNew, APIService)

from LmRex.tools.provider.bison import BisonAPI
from LmRex.tools.provider.gbif import GbifAPI
from LmRex.tools.provider.idigbio import IdigbioAPI
from LmRex.tools.provider.mopho import MorphoSourceAPI
from LmRex.tools.provider.specify import SpecifyPortalAPI
from LmRex.tools.utils import get_traceback

from LmRex.services.api.v1.base import _S2nService
from LmRex.services.api.v1.resolve import SpecifyResolve
from LmRex.services.api.v1.s2n_type import (print_s2n_output, S2nOutput, S2nKey)

# .............................................................................
@cherrypy.expose
class OccurrenceSvc(_S2nService):
    SERVICE_TYPE = APIService.Occurrence

    # ...............................................
    @classmethod
    def get_providers(self, filter_params=None):
        provnames = set()
        if filter_params is None:
            for p in ServiceProviderNew.all():
                if APIService.Occurrence in p[S2nKey.SERVICES]:
                    provnames.add(p[S2nKey.PARAM])
        # Fewer providers by dataset
        elif 'dataset_key' in filter_params.keys():
            provnames = set([ServiceProviderNew.GBIF[S2nKey.PARAM]])
        return provnames

    # ...............................................
    def _get_specify_records(self, occid, count_only):
        # Resolve for record URL
        spark = SpecifyResolve()
        solr_output = spark.get_specify_guid_meta(occid)
        (url, msg) = spark.get_url_from_meta(solr_output)
                
        if url is None:
            output = self.get_failure(query_term=occid, errors=[msg])
        else:
            try:
                output = SpecifyPortalAPI.get_specify_record(occid, url, count_only)
            except Exception as e:
                traceback = get_traceback()
                output = self.get_failure(query_term=occid, errors=[traceback])
        return output.response

    # ...............................................
    def _get_mopho_records(self, occid, count_only):
        try:
            output = MorphoSourceAPI.get_occurrences_by_occid_page1(
                occid, count_only=count_only)
        except Exception as e:
            traceback = get_traceback()
            output = self.get_failure(query_term=occid, errors=[traceback])
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
            output = self.get_failure(query_term=query_term, errors=[traceback])
        return output.response

    # ...............................................
    def get_records(self, occid, providers, count_only, filter_params={}):
        allrecs = []
        # Determine query
        query_term = 'invalid query term'
        dskey = None
        if occid is not None:
            query_term = occid
        elif filter_params:
            query_term = '{}'.format(filter_params)
            try:
                dskey = filter_params['dataset_key']
            except:
                pass
                
        for pr in providers:
            # Address single record
            if occid is not None:
                # GBIF
                if pr == ServiceProviderNew.GBIF[S2nKey.PARAM]:
                    gbif_output = self._get_gbif_records(occid, dskey, count_only)
                    allrecs.append(gbif_output)
                # iDigBio
                elif pr == ServiceProviderNew.iDigBio[S2nKey.PARAM]:
                    idb_output = self._get_idb_records(occid, count_only)
                    allrecs.append(idb_output)
                # MorphoSource
                elif pr == ServiceProviderNew.MorphoSource[S2nKey.PARAM]:
                    mopho_output = self._get_mopho_records(occid, count_only)
                    allrecs.append(mopho_output)
                # Specify
                elif pr == ServiceProviderNew.Specify[S2nKey.PARAM]:
                    sp_output = self._get_specify_records(occid, count_only)
                    allrecs.append(sp_output)
            # Filter by parameters
            elif filter_params:
                if dskey:
                    if pr == ServiceProviderNew.GBIF[S2nKey.PARAM]:
                        gbif_output = self._get_gbif_records(occid, dskey, count_only)
                        allrecs.append(gbif_output)

        # Assemble
        provstr = ', '.join(providers)
        full_out = S2nOutput(
            len(allrecs), query_term, APIService.Occurrence, provstr, 
            records=allrecs)
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
            LmRex.services.api.v1.S2nOutput object with optional records as a 
            list of dictionaries of records corresponding to specimen 
            occurrences in the provider database
        """
        try:
            filter_params = None
            usr_params = self._standardize_params(
                occid=occid, provider=provider, dataset_key=dataset_key, 
                count_only=count_only)
            # What to query: address one occurrence record, with optional filters
            occid = usr_params['occid']
            # What to query: common filters
            count_only = usr_params['count_only']
            if occid is None:
                # What to query: query for many records with filters
                dskey = usr_params['dataset_key']
                if dskey:
                    filter_params = {'dataset_key': dskey}
            # Who to query#     occids = ['dcb298f9-1ed3-11e3-bfac-90b11c41863e']
            req_providers = self.get_valid_requested_providers(
                usr_params['provider'], filter_params=filter_params)
            
            output = self.get_records(
                occid, req_providers, count_only, filter_params=filter_params)
        except Exception as e:
            traceback = get_traceback()
            output = self.get_failure(query_term=occid, errors=[traceback])
        return output.response
    
# # ......................................................................attelt.......
# @cherrypy.expose
# class _OccurrenceSvc(_S2nService):
#     SERVICE_TYPE = APIService.Occurrence
#     
# # .............................................................................
# @cherrypy.expose
# class OccGBIF(_OccurrenceSvc):
#     PROVIDER = ServiceProvider.GBIF
#     # ...............................................
#     def get_records(self, occid, count_only):
#         output = GbifAPI.get_occurrences_by_occid(
#             occid, count_only=count_only)
#         return output
# 
#     # ...............................................
#     @cherrypy.tools.json_out()
#     def GET(self, occid=None, count_only=False, **kwargs):
#         """Get one or more occurrence records for a dwc:occurrenceID from the 
#         GBIF occurrence record service.
#         
#         Args:
#             occid: an occurrenceID, a DarwinCore field intended for a globally 
#                 unique identifier (https://dwc.tdwg.org/list/#dwc_occurrenceID)
#             count_only: flag to indicate whether to return only a count, or 
#                 a count and records
#             kwargs: any additional keyword arguments are ignored
# 
#         Return:
#             LmRex.services.api.v1.S2nOutput object with optional records as a 
#             list of dictionaries of GBIF records corresponding to specimen 
#             occurrences in the GBIF database
#         """
#         try:
#             usr_params = self._standardize_params(occid=occid, count_only=count_only)
#             occurrence_id = usr_params['occid']
#             if occurrence_id is None:
#                 output = self._show_online()
#             else:
#                 output = self.get_records(occurrence_id, usr_params['count_only'])
#         except Exception as e:
#             output = self.get_failure(query_term=occid, errors=[str(e)])
#         return output.response
# 
# # .............................................................................
# @cherrypy.expose
# class OccIDB(_OccurrenceSvc):
#     PROVIDER = ServiceProvider.iDigBio
#     def get_records(self, occid, count_only):
#         output = IdigbioAPI.get_occurrences_by_occid(occid, count_only=count_only)
#         return output
# 
#     # ...............................................
#     @cherrypy.tools.json_out()
#     def GET(self, occid=None, count_only=False, **kwargs):
#         """Get one or more occurrence records for a dwc:occurrenceID from the
#         iDigBio occurrence record service.
#         
#         Args:
#             occid: an occurrenceID, a DarwinCore field intended for a globally 
#                 unique identifier (https://dwc.tdwg.org/list/#dwc_occurrenceID)
#             count_only: flag to indicate whether to return only a count, or 
#                 a count and records
#             kwargs: any additional keyword arguments are ignored
# 
#         Return:
#             LmRex.services.api.v1.S2nOutput object with optional records as a 
#             list of dictionaries of iDigBio records corresponding to specimen 
#             occurrences in the iDigBio database
#         """
#         try:
#             usr_params = self._standardize_params(occid=occid, count_only=count_only)
#             occurrence_id = usr_params['occid']
#             if occurrence_id is None:
#                 output = self._show_online()
#             else:
#                 output = self.get_records(occurrence_id, usr_params['count_only'])
#         except Exception as e:
#             output = self.get_failure(query_term=occid, errors=[str(e)])
#         return output.response
#     
# # .............................................................................
# @cherrypy.expose
# class OccMopho(_OccurrenceSvc):
#     PROVIDER = ServiceProvider.MorphoSource
#     # ...............................................
#     def get_records(self, occid, count_only):
#         output = MorphoSourceAPI.get_occurrences_by_occid_page1(
#             occid, count_only=count_only)
#         return output
# 
#     # ...............................................
#     @cherrypy.tools.json_out()
#     def GET(self, occid=None, count_only=False, **kwargs):
#         try:
#             usr_params = self._standardize_params(occid=occid, count_only=count_only)
#             occurrence_id = usr_params['occid']
#             if occurrence_id is None:
#                 output = self._show_online()
#             else:
#                 output = self.get_records(occurrence_id, usr_params['count_only'])
#         except Exception as e:
#             output = self.get_failure(query_term=occid, errors=[str(e)])
#         return output.response
#     
# # .............................................................................
# @cherrypy.expose
# class OccSpecify(_OccurrenceSvc):
#     PROVIDER = ServiceProvider.Specify
#     # ...............................................
#     def get_records(self, url, occid, count_only):
#         msg = 'Spocc failed: url = {}, occid = {}'.format(url, occid)
#         if url is None:
#             # Resolve for record URL
#             spark = SpecifyResolve()
#             solr_output = spark.get_specify_guid_meta(occid)
#             (url, msg) = spark.get_url_from_meta(solr_output)
#                 
#         if url is None:
#             output = self.get_failure(query_term=occid, errors=[msg])
#         else:
#             try:
#                 output = SpecifyPortalAPI.get_specify_record(occid, url, count_only)
#             except Exception as e:
#                 output = self.get_failure(query_term=occid, errors=[str(e)])
# 
# #         full_out = S2nOutput(
# #             out.count, occid, self.SERVICE_TYPE, self.PROVIDER[S2nKey.NAME],
# #             provider_query=out.provider_query, record_format=out.record_format, 
# #             records=out.records, errors=out.errors)
#         return output
#     
#     # ...............................................
#     @cherrypy.tools.json_out()
#     def GET(self, occid=None, url=None, count_only=False, **kwargs):
#         """Get one or more occurrence records for a dwc:occurrenceID from the
#         Specify occurrence record service.
#         
#         Args:
#             occid: an occurrenceID, a DarwinCore field intended for a globally 
#                 unique identifier (https://dwc.tdwg.org/list/#dwc_occurrenceID)
#             url: a URL to directly access the Specify record
#             count_only: flag to indicate whether to return only a count, or 
#                 a count and records
#             kwargs: any additional keyword arguments are ignored
# 
#         Return:
#             LmRex.services.api.v1.S2nOutput object with optional records as a 
#             list of dictionaries of Specify records corresponding to specimen 
#             occurrences in the Specify database
#         """
#         try:
#             usr_params = self._standardize_params(occid=occid, url=url)
#             if usr_params['url'] is None and usr_params['occid'] is None:
#                 output = self._show_online()
#             else:
#                 output = self.get_records(
#                     usr_params['url'], usr_params['occid'], count_only)
#         except Exception as e:
#             output = self.get_failure(query_term=occid, errors=[str(e)])
#         return output.response
    
# # .............................................................................
# @cherrypy.expose
# class OccTentacles(_OccurrenceSvc):
#     PROVIDER = ServiceProvider.S2N
#     # ...............................................
#     def get_records(self, usr_params):
# #         all_output = {S2nKey.COUNT: 0, S2nKey.RECORDS: []}
#         allrecs = []
#         
#         occid = usr_params['occid']
#         count_only = usr_params['count_only']
#         
#         # Specify ARK Record
#         spark = SpecifyResolve()
#         solr_output = spark.get_specify_guid_meta(occid)
#         (url, msg) = spark.get_url_from_meta(solr_output)
#         # Do not add GUID service record to occurrence records
#         
#         # Specify Record from URL in ARK
#         spocc = OccSpecify()
#         sp_output = spocc.get_records(url, occid, count_only)
#         allrecs.append(sp_output.response)
#         
#         # GBIF copy/s of Specify Record
#         gocc = OccGBIF()
#         gbif_output = gocc.get_records(occid, count_only)
#         allrecs.append(gbif_output.response)
#         
#         # iDigBio copy/s of Specify Record
#         idbocc = OccIDB()
#         idb_output = idbocc.get_records(occid, count_only)
#         allrecs.append(idb_output.response)
#         
#         # MorphoSource records connected to Specify Record
#         mopho = OccMopho()
#         mopho_output = mopho.get_records(occid, count_only)
#         allrecs.append(mopho_output.response)
# 
#         full_out = S2nOutput(
#             len(allrecs), occid, self.SERVICE_TYPE, self.PROVIDER[S2nKey.NAME],
#             records=allrecs)
#         return full_out
# 
#     # ...............................................
#     # ...............................................
#     @cherrypy.tools.json_out()
#     def GET(self, occid=None, count_only=False, **kwargs):
#         """Get one or more occurrence records for a dwc:occurrenceID from each
#         available occurrence record service.
#         
#         Args:
#             occid: an occurrenceID, a DarwinCore field intended for a globally 
#                 unique identifier (https://dwc.tdwg.org/list/#dwc_occurrenceID)
#             count_only: flag to indicate whether to return only a count, or 
#                 a count and records
#             kwargs: any additional keyword arguments are ignored
# 
#         Return:
#             a dictionary with keys for each service queried.  Values contain 
#             LmRex.services.api.v1.S2nOutput object with optional records as a 
#             list of dictionaries of records corresponding to specimen 
#             occurrences in the provider database
#         """
#         try:
#             usr_params = self._standardize_params(
#                 occid=occid, count_only=count_only)
#             output = self.get_records(usr_params)
#         except Exception as e:
#             output = self.get_failure(query_term=occid, errors=[str(e)])
#         return output.response

# .............................................................................
if __name__ == '__main__':
    from LmRex.common.lmconstants import TST_VALUES   
    occids = [TST_VALUES.GUIDS_W_SPECIFY_ACCESS[0]]
#     occids = ['dcb298f9-1ed3-11e3-bfac-90b11c41863e']
    dskeys = [TST_VALUES.DS_GUIDS_W_SPECIFY_ACCESS_RECS[0]]
    svc = OccurrenceSvc()
    # Query by occurrenceid
    for occid in occids:
        for count_only in [False]:
            for prov in svc.get_providers():
                out = svc.GET(
                    occid=occid, provider=prov, count_only=count_only)
                print_s2n_output(out)
    # Query by datasetid
    for dskey in dskeys:
        for count_only in [True]:
            for prov in svc.get_providers(filter_params={'dataset_key': dskey}):
                out = svc.GET(
                    occid=None, provider=prov, dataset_key=dskey, count_only=count_only)
                print_s2n_output(out)
