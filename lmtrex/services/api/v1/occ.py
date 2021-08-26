import cherrypy
from http import HTTPStatus

from lmtrex.common.lmconstants import (APIService, S2N_SCHEMA, ServiceProvider)
from lmtrex.common.s2n_type import (S2nKey, S2nOutput, print_s2n_output)

from lmtrex.tools.provider.gbif import GbifAPI
from lmtrex.tools.provider.idigbio import IdigbioAPI
from lmtrex.tools.provider.mopho import MorphoSourceAPI
from lmtrex.tools.provider.specify import SpecifyPortalAPI
from lmtrex.tools.provider.specify_resolver import SpecifyResolverAPI

from lmtrex.tools.utils import get_traceback

from lmtrex.services.api.v1.base import _S2nService

# .............................................................................
@cherrypy.expose
@cherrypy.popargs('occid')
class OccurrenceSvc(_S2nService):
    SERVICE_TYPE = APIService.Occurrence
    ORDERED_FIELDNAMES = S2N_SCHEMA.get_s2n_fields(APIService.Occurrence['endpoint'])

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
        spark = SpecifyResolverAPI()
        api_url = spark.resolve_guid_to_url(occid)
                
        try:
            output = SpecifyPortalAPI.get_specify_record(occid, api_url, count_only)
        except Exception as e:
            traceback = get_traceback()
            output = SpecifyPortalAPI.get_api_failure(
                self.SERVICE_TYPE['endpoint'], HTTPStatus.INTERNAL_SERVER_ERROR, 
                errinfo={'error': [traceback]})
        else:
            output.set_value(S2nKey.RECORD_FORMAT, self.SERVICE_TYPE[S2nKey.RECORD_FORMAT])
            output.format_records(self.ORDERED_FIELDNAMES)
        return output.response

    # ...............................................
    def _get_mopho_records(self, occid, count_only):
        try:
            output = MorphoSourceAPI.get_occurrences_by_occid_page1(
                occid, count_only=count_only)
        except Exception as e:
            traceback = get_traceback()
            output = MorphoSourceAPI.get_api_failure(
                self.SERVICE_TYPE['endpoint'], HTTPStatus.INTERNAL_SERVER_ERROR, 
                errinfo={'error': [traceback]})
        else:
            output.set_value(S2nKey.RECORD_FORMAT, self.SERVICE_TYPE[S2nKey.RECORD_FORMAT])
            output.format_records(self.ORDERED_FIELDNAMES)
        return output.response

    # ...............................................
    def _get_idb_records(self, occid, count_only):
        try:
            output = IdigbioAPI.get_occurrences_by_occid(occid, count_only=count_only)
        except Exception as e:
            traceback = get_traceback()
            output = IdigbioAPI.get_api_failure(
                self.SERVICE_TYPE['endpoint'], HTTPStatus.INTERNAL_SERVER_ERROR, 
                errinfo={'error': [traceback]})
        else:
            output.set_value(S2nKey.RECORD_FORMAT, self.SERVICE_TYPE[S2nKey.RECORD_FORMAT])
            output.format_records(self.ORDERED_FIELDNAMES)
        return output.response


    # ...............................................
    def _get_gbif_records(self, occid, dataset_key, count_only):
        try:
            if occid is not None:
                output = GbifAPI.get_occurrences_by_occid(
                    occid, count_only=count_only)
            elif dataset_key is not None:
                output = GbifAPI.get_occurrences_by_dataset(
                    dataset_key, count_only)
        except Exception as e:
            traceback = get_traceback()
            output = GbifAPI.get_api_failure(
                self.SERVICE_TYPE['endpoint'], HTTPStatus.INTERNAL_SERVER_ERROR, 
                errinfo={'error': [traceback]})
        else:
            output.set_value(S2nKey.RECORD_FORMAT, self.SERVICE_TYPE[S2nKey.RECORD_FORMAT])
            output.format_records(self.ORDERED_FIELDNAMES)
        return output.response

    # ...............................................
    def get_records(self, occid, req_providers, count_only, dataset_key=None):
        allrecs = []
        # for response metadata
        query_term = None
        provstr = ','.join(req_providers)
        if occid is not None:
            query_term = 'occid={}&provider={}&count_only={}'.format(occid, provstr, count_only)
        elif dataset_key:
            try:
                query_term = 'dataset_key={}&provider={}&count_only={}'.format(dataset_key, provstr, count_only)
            except:
                pass

        for pr in req_providers:
            # Address single record
            if occid is not None:
                # GBIF
                if pr == ServiceProvider.GBIF[S2nKey.PARAM]:
                    gbif_output = self._get_gbif_records(occid, dataset_key, count_only)
                    allrecs.append(gbif_output)
                # iDigBio
                elif pr == ServiceProvider.iDigBio[S2nKey.PARAM]:
                    idb_output = self._get_idb_records(occid, count_only)
                    allrecs.append(idb_output)
                # MorphoSource
                elif pr == ServiceProvider.MorphoSource[S2nKey.PARAM]:
                    mopho_output = self._get_mopho_records(occid, count_only)
                    allrecs.append(mopho_output)
                # Specify
                elif pr == ServiceProvider.Specify[S2nKey.PARAM]:
                    sp_output = self._get_specify_records(occid, count_only)
                    allrecs.append(sp_output)
            # Filter by parameters
            elif dataset_key:
                if pr == ServiceProvider.GBIF[S2nKey.PARAM]:
                    gbif_output = self._get_gbif_records(occid, dataset_key, count_only)
                    allrecs.append(gbif_output)

        prov_meta = self._get_s2n_provider_response_elt(query_term=query_term)
        # Assemble
        # TODO: Figure out why errors are retained from query to query!!!  Resetting to {} works.
        full_out = S2nOutput(
            len(allrecs), self.SERVICE_TYPE['endpoint'], provider=prov_meta, 
            records=allrecs, errors={})
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
        error_description = None
        http_status = int(HTTPStatus.OK)
        
        valid_providers = self.get_valid_providers()
        if occid is None and dataset_key is None:
            output = self._show_online(valid_providers)
        else:   
            # No filter_params defined for Name service yet
            try:
                good_params, errinfo = self._standardize_params(
                occid=occid, provider=provider, dataset_key=dataset_key, 
                count_only=count_only)
                # Bad parameters
                try:
                    error_description = '; '.join(errinfo['error'])                            
                    http_status = int(HTTPStatus.BAD_REQUEST)
                except:
                    pass
                    
            except Exception as e:
                http_status = int(HTTPStatus.INTERNAL_SERVER_ERROR)
                error_description = get_traceback()
                
            else:  
                if http_status != HTTPStatus.BAD_REQUEST:
                    # Do Query!
                    try:
                        output = self.get_records(
                            good_params['occid'], good_params['provider'], good_params['count_only'], 
                            dataset_key=good_params['dataset_key'])
    
                        # Add message on invalid parameters to output
                        try:
                            for err in errinfo['warning']:
                                output.append_error('warning', err)
                        except:
                            pass
                            
                    except Exception as e:
                        http_status = int(HTTPStatus.INTERNAL_SERVER_ERROR)
                        error_description = get_traceback()

        if http_status == HTTPStatus.OK:
            return output.response
        else:
            raise cherrypy.HTTPError(http_status, error_description)
    

# .............................................................................
if __name__ == '__main__':
    from lmtrex.common.lmconstants import TST_VALUES
    # occids = TST_VALUES.GUIDS_WO_SPECIFY_ACCESS[0:3]
    occids = ['84fe1494-c378-4657-be15-8c812b228bf4', 
              '04c05e26-4876-4114-9e1d-984f78e89c15', 
              '2facc7a2-dd88-44af-b95a-733cc27527d4']
    occids = ['01493b05-4310-4f28-9d81-ad20860311f3', '01559f57-62ca-45ba-80b1-d2aafdc46f44', 
              '015f35b8-655a-4720-9b88-c1c09f6562cb', '016613ba-4e65-44d5-94d1-e24605afc7e1', 
              '0170cead-c9cd-48ba-9819-6c5d2e59947e', '01792c67-910f-4ad6-8912-9b1341cbd983', 
              '017ea8f2-fc5a-4660-92ec-c203daaaa631', '018728bb-c376-4562-9ccb-8e3c3fd70df6', 
              '018a34a9-55da-4503-8aee-e728ba4be146', '019b547a-79c7-47b3-a5ae-f11d30c2b0de']
    
    dskeys = [TST_VALUES.DS_GUIDS_W_SPECIFY_ACCESS_RECS[0]]
    svc = OccurrenceSvc()
    out = svc.GET(dataset_key=dskeys[0], provider='gbif', count_only=True)
    # out = svc.GET(occid='test', provider='mopho', count_only=False)
    # out = svc.GET(occid='2facc7a2-dd88-44af-b95a-733cc27527d4', provider='gbif', count_only=False)
    
    prov = 'gbif'
    for occid in occids:
        out = svc.GET(occid=occid, provider=prov, count_only=False)
        outputs = out['records']
        print_s2n_output(out, do_print_rec=True)
    
    x = 1
    
"""
https://broker-dev.spcoco.org/api/v1/frontend/?occid=2c1becd5-e641-4e83-b3f5-76a55206539a
"""