from collections import OrderedDict
from http import HTTPStatus
import pykew.ipni as ipni
from pykew.ipni_terms import Name
import urllib

from lmtrex.common.lmconstants import (
    ENCODING, ServiceProvider, URL_ESCAPES, WORMS)
from lmtrex.common.s2n_type import S2nEndpoint, S2nOutput, S2nSchema

from lmtrex.tools.provider.api import APIQuery
from lmtrex.tools.utils  import get_traceback

# .............................................................................
class IpniAPI(APIQuery):
    """Class to query WoRMS API for a name match
    
    Todo:
        Extend for other services
    """
    PROVIDER = ServiceProvider.IPNI
    # NAME_MAP = S2nSchema.get_ipni_name_map()
    
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
    def _standardize_record(cls, rec, is_accepted=False):
        newrec = {}
        data_std_fld = S2nSchema.get_data_url_fld()
        prov_sciname_fn = 'valid_authority'
        prov_canname_fn = 'valid_name'
        hierarchy_fld = 'hierarchy'
        
        # Assemble scientific name
        try:
            auth_str = rec['valid_authority']
        except:
            if is_accepted is False:
                auth_str = rec['authority']
            else:
                auth_str = ''
        try:
            canonical_str = rec['valid_name']
        except:
            if is_accepted is False:
                canonical_str = rec['name']
            else:
                canonical_str = ''
        sciname_str = '{}{}'.format(canonical_str, auth_str)
            
        for stdfld, provfld in cls.NAME_MAP.items():
            try:
                val = rec[provfld]
            except:
                val = None
                
            # Special cases
            if provfld == prov_sciname_fn:
                newrec[stdfld] = sciname_str
                
            elif provfld == prov_canname_fn:
                newrec[stdfld] = canonical_str
                
            # Use ID field to construct data_url
            elif provfld == WORMS.ID_FLDNAME:
                newrec[stdfld] = val
                newrec[data_std_fld] = WORMS.get_species_data(val)

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
                
            # all others, including view_url
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
    def _standardize_output(
            cls, output, service, query_status=None, query_urls=[], is_accepted=False, errinfo={}):
        """
        list of lists of dictionaries
        """
        total = 0
        stdrecs = []
        # output is a list of lists of dictionaries
        for taxconcept_lst in output:
            for rec in taxconcept_lst:
                total +=1
                newrec = cls._standardize_record(rec, is_accepted=is_accepted)
                if newrec:
                    stdrecs.append(newrec)
        prov_meta = cls._get_provider_response_elt(query_status=query_status, query_urls=query_urls)
        std_output = S2nOutput(
            total, service, provider=prov_meta, records=stdrecs, errors=errinfo)
        
        return std_output
    

    # ...............................................
    @classmethod
    def match_name(cls, namestr, is_accepted=False, logger=None):
        """Return closest accepted species in IPNI taxonomy,
        
        Args:
            namestr: A scientific namestring possibly including author, year, 
                rank marker or other name information.
            is_accepted: match the ACCEPTED TaxonomicStatus 
                
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
        
        query = { Name.genus: 'Poa', Name.species: 'annua' }
        res = ipni.search(query)

        
        api = IpniAPI(name_clean, other_filters={'marine_only': 'false'}, logger=logger)
        
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
            std_output = cls._standardize_output(
                api.output, S2nEndpoint.Name, query_status=api.status_code, query_urls=[api.url], 
                is_accepted=is_accepted, errinfo=errinfo)
            
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


"""
import pykew.ipni as ipni
import pykew.powo as powo

from pykew.ipni_terms import Name
from pykew.powo_terms import Filter

gn = 'Poa'
sp = 'annua'

can = '{} {}'.format(gn, sp)
filter = { Name.genus: 'Poa', Name.species: 'annua' }

res1 = ipni.search(can)
res2 = ipni.search(filter)


"""