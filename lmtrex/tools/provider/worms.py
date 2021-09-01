from collections import OrderedDict
from http import HTTPStatus
import os
import requests
import urllib

from lmtrex.common.issue_definitions import ISSUE_DEFINITIONS
from lmtrex.common.lmconstants import (
    ENCODING, GBIF, ServiceProvider, URL_ESCAPES, WORMS)
from lmtrex.common.s2n_type import S2nEndpoint, S2nKey, S2nOutput, S2nSchema
from lmtrex.fileop.logtools import (log_info, log_error)


from lmtrex.tools.provider.api import APIQuery
from lmtrex.tools.utils  import get_traceback, add_errinfo

# .............................................................................
class WormsAPI(APIQuery):
    """Class to query WoRMS API for a name match
    
    Todo:
        Extend for other services
    """
    PROVIDER = ServiceProvider.WoRMS
    NAME_MAP = S2nSchema.get_worms_name_map()
    
    # ...............................................
    def __init__(self, name, other_filters={}, logger=None):
        """
        Constructor for WormsAPI class
        
        Args:
            other_filters: optional filters
            logger: optional logger for info and error messages.  If None, 
                prints to stdout
        """
        url = '{}/{}'.format(WORMS.REST_URL, WORMS.NAME_MATCH_SERVICE)
        other_filters[WORMS.MATCH_PARAM] = name
        try:
            other_filters[WORMS.FILTER_PARAM]
        except:
            other_filters[WORMS.FILTER_PARAM] = False
        APIQuery.__init__(self, url, other_filters=other_filters, logger=logger)

    # ...............................................
    def _assemble_filter_string(self, filter_string=None):
        # Assemble key/value pairs
        if filter_string is None:
            all_filters = self._other_filters.copy()
            if self._q_filters:
                q_val = self._assemble_q_val(self._q_filters)
                all_filters[self._q_key] = q_val
            for k, val in all_filters.items():
                if isinstance(val, bool):
                    val = str(val).lower()
                # works for GBIF, iDigBio, ITIS web services (no manual escaping)
                all_filters[k] = str(val).encode(ENCODING)
            filter_string = urllib.parse.urlencode(all_filters)
        # Escape filter string
        else:
            for oldstr, newstr in URL_ESCAPES:
                filter_string = filter_string.replace(oldstr, newstr)
        return filter_string

    # ...............................................
    @classmethod
    def _get_output_val(cls, out_dict, name):
        try:
            tmp = out_dict[name]
            val = str(tmp).encode(ENCODING)
        except Exception:
            return None
        return val
    
    # ...............................................
    @classmethod
    def _standardize_name_record(cls, rec):
        newrec = {}
        data_std_fld = S2nSchema.get_data_url()
        hierarchy_fld = 'hierarchy'
        
        for stdfld, provfld in cls.NAME_MAP.items():
            try:
                val = rec[provfld]
            except:
                val = None
            # Also use ID field to construct URLs
            if stdfld == 's2n:scientific_name':
                try:
                    auth_str = rec['valid_authority']
                    newrec[stdfld] = '{}{}'.format(val, auth_str)
                except:
                    newrec[stdfld] = val
                    
            elif stdfld == data_std_fld:
                try:
                    key = rec['valid_AphiaID']
                    newrec[stdfld] = WORMS.get_species_data(key)
                except:
                    newrec[stdfld] = None

            # Assemble from other fields
            elif provfld == hierarchy_fld:
                hierarchy = OrderedDict()
                for rnk in S2nSchema.RANKS:
                    try:
                        val = rec[rnk]
                    except:
                        pass
                    else:
                        hierarchy[rnk] = val
                newrec[stdfld] = [hierarchy]
                
            # all others
            else:
                newrec[stdfld] = val
        return newrec
    
    # ...............................................
    @classmethod
    def _test_record(cls, status, rec):
        is_good = False
        # No filter by status, take original
        if status is None:
            is_good = True
        else:
            outstatus = None
            try:
                outstatus = rec['status'].lower()
            except AttributeError:
                print(cls._get_error_message(msg='No status in record'))
            else:
                if outstatus == status:
                    is_good = True
        return is_good

    # ...............................................
    @classmethod
    def match_name(cls, namestr, is_accepted=False, logger=None):
        """Return closest accepted species in WoRMS taxonomy,
        
        Args:
            namestr: A scientific namestring possibly including author, year, 
                rank marker or other name information.
            is_accepted: match the ACCEPTED TaxonomicStatus in the GBIF record
                
        Returns:
            Either a dictionary containing a matching record with status 
                'accepted' or 'synonym' without 'alternatives'.  
            Or, if there is no matching record, return the first/best 
                'alternative' record with status 'accepted' or 'synonym'.
        """
        status = None
        errinfo = {}
        if is_accepted:
            status = 'accepted'
        name_clean = namestr.strip()
        other_filters = {'name': name_clean, 'verbose': 'true'}
        api = WormsAPI(
            service=GBIF.SPECIES_SERVICE, key='match',
            other_filters=other_filters, logger=logger)
        
        try:
            api.query()
        except Exception as e:
            tb = get_traceback()
            errinfo['error'] =  [cls._get_error_message(err=tb)]
            std_output = cls.get_api_failure(
                S2nEndpoint.Name, HTTPStatus.INTERNAL_SERVER_ERROR, errinfo=errinfo)
        else:
            if api.error:
                errinfo['error'] =  [api.error]
            # Standardize output from provider response
            std_output = cls._standardize_match_output(
                api.output, status, api.status_code, query_urls=[api.url], errinfo=errinfo)
            
        return std_output





    # ...............................................
    def query(self):
        """ Queries the API and sets 'output' attribute to a ElementTree object
        """
        APIQuery.query_by_get(self, output_type='json')





# .............................................................................
if __name__ == '__main__':
    # test
    pass