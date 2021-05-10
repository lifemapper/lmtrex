from lmtrex.common.lmconstants import (
    APIService, DWC, JSON_HEADERS, ServiceProvider, S2N_SCHEMA, TST_VALUES)
from lmtrex.services.api.v1.s2n_type import S2nKey, S2nOutput
from lmtrex.tools.provider.api import APIQuery

# .............................................................................
class SpecifyPortalAPI(APIQuery):
    """Class to query Specify portal APIs and return results"""
    PROVIDER = ServiceProvider.Specify[S2nKey.NAME]
    PROVIDER_S2N_MAPPING = S2N_SCHEMA.get_specify_occurrence_mapping()
    # ...............................................
    def __init__(self, url=None, logger=None):
        """Constructor for SpecifyPortalAPI class"""
        if url is None:
            url = 'http://preview.specifycloud.org/export/record'
        APIQuery.__init__(self, url, headers=JSON_HEADERS, logger=logger)

    # ...............................................
    @classmethod
    def _standardize_record(cls, rec):
        newrec = {}
        for fldname, val in rec:
            if fldname in cls.PROVIDER_S2N_MAPPING.keys():
                newfldname = cls.PROVIDER_S2N_MAPPING[fldname]
                newrec[newfldname] = val
        return newrec
                
    # ...............................................
    @classmethod
    def _standardize_output(
            cls, output, query_term, service, provider_query=[], count_only=False, err=None):
        stdrecs = []
        total = 0
        errmsgs = []
        if err is not None:
            errmsgs.append(err)
        # Count
        if output:
            try:
                rec = output['core']
            except Exception as e:
                errmsgs.append(cls._get_error_message(err=e))
            else:
                total = 1
                # Records
                if not count_only:
                    try:
                        stdrecs.append(cls._standardize_record(rec))
                    except Exception as e:
                        msg = cls._get_error_message(err=e)
                        errmsgs.append(msg)
        std_output = S2nOutput(
            total, query_term, service, cls.PROVIDER, 
            provider_query=provider_query, record_format=DWC.SCHEMA, 
            records=stdrecs, errors=errmsgs)

        return std_output

    # ...............................................
    @classmethod
    def get_specify_record(cls, occid, url, count_only, logger=None):
        """Return Specify record published at this url.  
        
        Args:
            url: direct url endpoint for source Specify occurrence record
            
        Note:
            Specify records/datasets without a server endpoint may be cataloged
            in the Solr Specify Resolver but are not resolvable to the host 
            database.  URLs returned for these records begin with 'unknown_url'.
        """
        if url is None:
            std_output = cls._standardize_output(
                {}, occid, APIService.Occurrence, provider_query=[], 
                count_only=count_only, err='No URL to Specify record')
        elif url.startswith('http'):
            api = APIQuery(url, headers=JSON_HEADERS, logger=logger)
    
            try:
                api.query_by_get()
            except Exception as e:
                std_output = cls.get_failure(errors=[cls._get_error_message(err=e)])
            # Standardize output from provider response
            std_output = cls._standardize_output(
                api.output, occid, APIService.Occurrence, 
                provider_query=[url], count_only=count_only, err=api.error)
        
        return std_output
