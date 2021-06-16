from lmtrex.common.lmconstants import (
    APIService, DWC, JSON_HEADERS, ServiceProvider, S2N_SCHEMA)
from lmtrex.services.api.v1.s2n_type import S2nKey, S2nOutput
from lmtrex.tools.provider.api import APIQuery

# .............................................................................
class SpecifyPortalAPI(APIQuery):
    """Class to query Specify portal APIs and return results"""
    PROVIDER = ServiceProvider.Specify[S2nKey.NAME]
    OCCURRENCE_MAP = S2N_SCHEMA.get_specify_occurrence_map()
    # ...............................................
    def __init__(self, url=None, logger=None):
        """Constructor for SpecifyPortalAPI class"""
        if url is None:
            url = 'http://preview.specifycloud.org/export/record'
        APIQuery.__init__(self, url, headers=JSON_HEADERS, logger=logger)

    # ...............................................
    @classmethod
    def _standardize_sp7_record(cls, rec):
        newrec = {}
        to_str_fields = ['dwc:year', 'dwc:month', 'dwc:day']
        for fldname, val in rec:
            # Leave out fields without value
            if val and fldname in cls.OCCURRENCE_MAP.keys():
                newfldname = cls.OCCURRENCE_MAP[fldname]
                # Modify int date elements to string (to match iDigBio)
                if newfldname in to_str_fields:
                    newrec[newfldname] = str(val)
                else:
                    newrec[newfldname] = val
        return newrec
                
    # ...............................................
    @classmethod
    def _standardize_sp6_record(cls, rec):
        newrec = {}
        mapping = S2N_SCHEMA.get_specifycache_occurrence_map()
        for fldname, val in rec.items():
            # Leave out fields without value
            if val:
                # Leave out non-mapped fields
                try:
                    newfldname = mapping[fldname]
                    newrec[newfldname] = val
                except:
                    pass
        return newrec
                
    # ...............................................
    @classmethod
    def _standardize_output(
            cls, output, query_term, service, provider_query=[], count_only=False, err={}):
        stdrecs = []
        total = 0
        is_specify_cache = False
        errmsgs = []
        if err:
            errmsgs.append(err)
        # Count
        if output:
            try:
                # Specify 7 record
                rec = output['core']
            except Exception as e:
                rec = output
                is_specify_cache = True
                
            if rec:
                total = 1
                # Records
                if not count_only:
                    if is_specify_cache:
                        stdrecs.append(cls._standardize_sp6_record(rec))
                    else:
                        stdrecs.append(cls._standardize_sp7_record(rec))
                        
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
            
        Note:                # Leave out fields without value

            Specify records/datasets without a server endpoint may be cataloged
            in the Solr Specify Resolver but are not resolvable to the host 
            database.  URLs returned for these records begin with 'unknown_url'.
        """
        if url is None:
            std_output = cls._standardize_output(
                {}, occid, APIService.Occurrence['endpoint'], provider_query=[], 
                count_only=count_only, err='No URL to Specify record')
        elif url.startswith('http'):
            api = APIQuery(url, headers=JSON_HEADERS, logger=logger)
    
            try:
                api.query_by_get()
            except Exception as e:
                std_output = cls.get_failure(errors=[{'error': cls._get_error_message(err=e)}])
            api_err = None
            if api.error:
                api_err = {'error': api.error}
            # Standardize output from provider response
            std_output = cls._standardize_output(
                api.output, occid, APIService.Occurrence['endpoint'], 
                provider_query=[url], count_only=count_only, err=api_err)
        
        return std_output
