from http import HTTPStatus
from markupsafe import escape
from werkzeug.exceptions import (BadRequest, InternalServerError)


from lmtrex.common.lmconstants import (APIService, ServiceProvider)
from lmtrex.common.s2n_type import (S2nKey, S2nOutput, S2nSchema, print_s2n_output)

from lmtrex.tools.provider.gbif import GbifAPI
from lmtrex.tools.provider.idigbio import IdigbioAPI
from lmtrex.tools.provider.mopho import MorphoSourceAPI
from lmtrex.tools.provider.specify import SpecifyPortalAPI
from lmtrex.tools.provider.specify_resolver import SpecifyResolverAPI

from lmtrex.tools.utils import get_traceback

from lmtrex.flask_app.broker.base import _S2nService

# .............................................................................
class OccurrenceSvc(_S2nService):
    SERVICE_TYPE = APIService.Occurrence
    ORDERED_FIELDNAMES = S2nSchema.get_s2n_fields(APIService.Occurrence['endpoint'])

    # ...............................................
    @classmethod
    def get_providers(cls, filter_params=None):
        """Note: Overrides _S2nService.get_providers"""
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
    @classmethod
    def _get_specify_records(cls, occid, count_only):
        # Resolve for record URL
        spark = SpecifyResolverAPI()

        api_url = spark.resolve_guid_to_url(occid)
                
        try:
            output = SpecifyPortalAPI.get_specify_record(occid, api_url, count_only)
        except Exception as e:
            traceback = get_traceback()
            output = SpecifyPortalAPI.get_api_failure(
                cls.SERVICE_TYPE['endpoint'], HTTPStatus.INTERNAL_SERVER_ERROR, 
                errinfo={'error': [traceback]})
        else:
            output.set_value(S2nKey.RECORD_FORMAT, cls.SERVICE_TYPE[S2nKey.RECORD_FORMAT])
            output.format_records(cls.ORDERED_FIELDNAMES)
        return output.response

    # ...............................................
    @classmethod
    def _get_mopho_records(cls, occid, count_only):
        try:
            output = MorphoSourceAPI.get_occurrences_by_occid_page1(
                occid, count_only=count_only)
        except Exception as e:
            traceback = get_traceback()
            output = MorphoSourceAPI.get_api_failure(
                cls.SERVICE_TYPE['endpoint'], HTTPStatus.INTERNAL_SERVER_ERROR, 
                errinfo={'error': [traceback]})
        else:
            output.set_value(S2nKey.RECORD_FORMAT, cls.SERVICE_TYPE[S2nKey.RECORD_FORMAT])
            output.format_records(cls.ORDERED_FIELDNAMES)
        return output.response

    # ...............................................
    @classmethod
    def _get_idb_records(cls, occid, count_only):
        try:
            output = IdigbioAPI.get_occurrences_by_occid(occid, count_only=count_only)
        except Exception as e:
            traceback = get_traceback()
            output = IdigbioAPI.get_api_failure(
                cls.SERVICE_TYPE['endpoint'], HTTPStatus.INTERNAL_SERVER_ERROR, 
                errinfo={'error': [traceback]})
        else:
            output.set_value(S2nKey.RECORD_FORMAT, cls.SERVICE_TYPE[S2nKey.RECORD_FORMAT])
            output.format_records(cls.ORDERED_FIELDNAMES)
        return output.response


    # ...............................................
    @classmethod
    def _get_gbif_records(cls, occid, dataset_key, count_only):
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
                cls.SERVICE_TYPE['endpoint'], HTTPStatus.INTERNAL_SERVER_ERROR, 
                errinfo={'error': [traceback]})
        else:
            output.set_value(S2nKey.RECORD_FORMAT, cls.SERVICE_TYPE[S2nKey.RECORD_FORMAT])
            output.format_records(cls.ORDERED_FIELDNAMES)
        return output.response

    # ...............................................
    @classmethod
    def _get_records(cls, occid, req_providers, count_only, dataset_key=None):
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
                    gbif_output = cls._get_gbif_records(occid, dataset_key, count_only)
                    allrecs.append(gbif_output)
                # iDigBio
                elif pr == ServiceProvider.iDigBio[S2nKey.PARAM]:
                    idb_output = cls._get_idb_records(occid, count_only)
                    allrecs.append(idb_output)
                # MorphoSource
                elif pr == ServiceProvider.MorphoSource[S2nKey.PARAM]:
                    mopho_output = cls._get_mopho_records(occid, count_only)
                    allrecs.append(mopho_output)
                # Specify
                elif pr == ServiceProvider.Specify[S2nKey.PARAM]:
                    sp_output = cls._get_specify_records(occid, count_only)
                    allrecs.append(sp_output)
            # Filter by parameters
            elif dataset_key:
                if pr == ServiceProvider.GBIF[S2nKey.PARAM]:
                    gbif_output = cls._get_gbif_records(occid, dataset_key, count_only)
                    allrecs.append(gbif_output)

        prov_meta = cls._get_s2n_provider_response_elt(query_term=query_term)
        # Assemble
        # TODO: Figure out why errors are retained from query to query!!!  Resetting to {} works.
        full_out = S2nOutput(
            len(allrecs), cls.SERVICE_TYPE['endpoint'], provider=prov_meta, 
            records=allrecs, errors={})
        return full_out

    # ...............................................
    @classmethod
    def get_test(cls, occid=None, **kwargs):
        return f"Testing occid, {escape(occid)}!"

    # ...............................................
    @classmethod
    def get_endpoint(cls, **kwargs):
        try:
            valid_providers = cls._get_valid_providers()
            output = cls._show_online(valid_providers)
        except Exception as e:
            raise
        return output.response

    # ...............................................
    @classmethod
    def get_occurrence_records(cls, occid=None, provider=None, dataset_key=None, count_only=False, **kwargs):
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
        if occid is None and dataset_key is None:
            return cls.get_endpoint()
        else:   
            # No filter_params defined for Name service yet
            try:
                good_params, errinfo = cls._standardize_params(
                    occid=occid, provider=provider, dataset_key=dataset_key, count_only=count_only)
                # Bad parameters
                try:
                    error_description = '; '.join(errinfo['error'])
                    raise BadRequest(error_description)
                except:
                    pass
                    
            except Exception as e:
                error_description = get_traceback()
                raise InternalServerError(error_description)
                
            # Do Query!
            try:
                output = cls._get_records(
                    good_params['occid'], good_params['provider'], good_params['count_only'], 
                    dataset_key=good_params['dataset_key'])

                # Add message on invalid parameters to output
                try:
                    for err in errinfo['warning']:
                        output.append_error('warning', err)
                except:
                    pass
                    
            except Exception as e:
                error_description = get_traceback()
                raise InternalServerError(error_description)

        return output.response
    

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
    # This occ has 16 issues in IDB, 0 in GBIF
    occids = ['2facc7a2-dd88-44af-b95a-733cc27527d4', '2c1becd5-e641-4e83-b3f5-76a55206539a']
    occids = ['bffe655b-ea32-4838-8e80-a80e391d5b11']
    occids = ['db193603-1ed3-11e3-bfac-90b11c41863e']
    
    svc = OccurrenceSvc()
    out = svc.get_endpoint()
    
    for occid in occids:
        out = svc.get_occurrence_records(occid=occid, provider=None, count_only=False)
        outputs = out['records']
        print_s2n_output(out, do_print_rec=True)
    
    x = 1
    
"""
https://broker-dev.spcoco.org/api/v1/frontend/?occid=2c1becd5-e641-4e83-b3f5-76a55206539a
https://broker.spcoco.org/api/v1/occ/ed8cfa5a-7b47-11e4-8ef3-782bcb9cd5b5
https://broker-dev.spcoco.org/api/v1/occ/ed8cfa5a-7b47-11e4-8ef3-782bcb9cd5b5

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

