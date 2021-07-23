from http import HTTPStatus

from lmtrex.common.lmconstants import (
    APIService, MorphoSource, ServiceProvider, TST_VALUES, S2N_SCHEMA)
from lmtrex.fileop.logtools import (log_info)
from lmtrex.services.api.v1.s2n_type import S2nKey
from lmtrex.tools.provider.api import APIQuery
from lmtrex.tools.utils import add_errinfo, get_traceback

# .............................................................................
class MorphoSourceAPI(APIQuery):
    """Class to query Specify portal APIs and return results"""
    PROVIDER = ServiceProvider.MorphoSource
    OCCURRENCE_MAP = S2N_SCHEMA.get_mopho_occurrence_map()
    
    # ...............................................
    def __init__(
            self, resource=MorphoSource.OCC_RESOURCE, q_filters={}, 
            other_filters={}, logger=None):
        """Constructor for MorphoSourceAPI class"""
        url = '{}/{}/{}'.format(
            MorphoSource.REST_URL, MorphoSource.COMMAND, resource)
        APIQuery.__init__(
            self, url, q_filters=q_filters, 
            other_filters=other_filters, logger=logger)

    # ...............................................
    @classmethod
    def _standardize_record(cls, rec):
        newrec = {}
        # Add provider stuff
        for fldname, val in rec.items():
            # Leave out fields without value
            if fldname in cls.OCCURRENCE_MAP.keys():
                # Use DWC field to also construct api URL
                if fldname == MorphoSource.DWC_ID_FIELD:
                    url_stdfld = cls.OCCURRENCE_MAP['api_url']
                    newrec[url_stdfld] = MorphoSource.get_occurrence_data(val)
                # Use local ID field to also construct webpage url
                elif fldname == MorphoSource.LOCAL_ID_FIELD:
                    url_stdfld = cls.OCCURRENCE_MAP['view_url']
                    newrec[url_stdfld] = MorphoSource.get_occurrence_view(val)
                    
                stdfld = cls.OCCURRENCE_MAP[fldname]
                newrec[stdfld] =  val
        return newrec
    
    # ...............................................
    @classmethod
    def get_occurrences_by_occid_page1(cls, occid, count_only=False, logger=None):
        start = 0
        errinfo = {}
        api = MorphoSourceAPI(
            resource=MorphoSource.OCC_RESOURCE, 
            q_filters={MorphoSource.OCCURRENCEID_KEY: occid},
            other_filters={'start': start, 'limit': MorphoSource.LIMIT})
        # Handle bad SSL certificate on old MorphoSource API until v2 is working
        verify=True
        if api.url.index(MorphoSource.REST_URL) >= 0:
            verify=False
        try:
            api.query_by_get(verify=verify)
        except Exception as e:
            tb = get_traceback()
            errinfo = add_errinfo(errinfo, 'error', cls._get_error_message(err=tb))
            std_out = cls.get_api_failure(
                APIService.Occurrence['endpoint'], HTTPStatus.INTERNAL_SERVER_ERROR, errinfo=errinfo)
        else:
            # Standardize output from provider response
            query_term = 'occid={}&count_only={}'.format(occid, count_only)
            if api.error:
                errinfo['error'] =  [api.error]

            std_out = cls._standardize_output(
                api.output, MorphoSource.TOTAL_KEY, MorphoSource.RECORDS_KEY, 
                MorphoSource.RECORD_FORMAT, query_term, APIService.Occurrence['endpoint'], 
                query_status=api.status_code, query_urls=[api.url], count_only=count_only, 
                err=errinfo)
        
        return std_out

# .............................................................................
if __name__ == '__main__':
    # test
    
    for guid in TST_VALUES.GUIDS_WO_SPECIFY_ACCESS:
        moutput = MorphoSourceAPI.get_occurrences_by_occid_page1(guid)
        for r in moutput.response[S2nKey.RECORDS]:
            occid = notes = None
            try:
                occid = r['specimen.occurrence_id']
                notes = r['specimen.notes']
            except Exception as e:
                msg = 'Morpho source record exception {}'.format(e)
            else:
                msg = '{}: {}'.format(occid, notes)
            log_info(msg)

"""
https://ms1.morphosource.org/api/v1/find/specimens?start=0&limit=1000&q=occurrence_id%3Aed8cfa5a-7b47-11e4-8ef3-782bcb9cd5b5'
url = 'https://ea-boyerlab-morphosource-01.oit.duke.edu/api/v1/find/specimens?start=0&limit=1000&q=occurrence_id%3Aed8cfa5a-7b47-11e4-8ef3-782bcb9cd5b5'
"""