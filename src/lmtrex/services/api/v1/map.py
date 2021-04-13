import cherrypy

from lmtrex.common.lmconstants import (
    ServiceProviderNew, APIService, Lifemapper, TST_VALUES)
from lmtrex.services.api.v1.base import _S2nService
from lmtrex.services.api.v1.name import NameSvc
from lmtrex.services.api.v1.s2n_type import (S2nKey, S2nOutput, print_s2n_output)
from lmtrex.tools.provider.lifemapper import LifemapperAPI

# .............................................................................
@cherrypy.expose
class MapSvc(_S2nService):
    SERVICE_TYPE = APIService.Map
    
    # ...............................................
    @classmethod
    def get_providers(self, search_params=None):
        provnames = set()
        # Ignore as-yet undefined search_params
        for p in ServiceProviderNew.all():
            if APIService.Name in p[S2nKey.SERVICES]:
                provnames.add(p[S2nKey.PARAM])
        return provnames

    # ...............................................
    def _get_lifemapper_records(self, namestr, scenariocode, color, do_match):
        # First: get name(s)
        if do_match is False:
            scinames = [namestr] 
        else:
            gan = NameSvc()
            gout = gan.GET(
                namestr=namestr, gbif_accepted=True, do_count=False, do_parse=True)
            good_names = gout['records']
            # Lifemapper archive only uses GBIF Backbone Taxonomy accepted names
            # If no gbif_accepted names, try provided namestr
            scinames = []        
            if len(good_names) == 0:
                scinames.append(namestr)
            else:
                for namerec in good_names:
                    try:
                        scinames.append(namerec['scientificName'])
                    except Exception as e:
                        print('No scientificName element in GBIF record {} for {}'
                              .format(namerec, namestr))
        # Second: get completed Lifemapper projections (map layers)
        stdrecs = []
        errmsgs = []
        queries = []
        for sname in scinames:
            # TODO: search on occurrenceset, then also pull projection layers
            lout = LifemapperAPI.find_map_layers_by_name(
                sname, prjscenariocode=scenariocode, color=color)
            stdrecs.extend(lout.records)
            errmsgs.extend(lout.errors)
            queries.extend(lout.provider_query)
        
        full_out = S2nOutput(
            len(stdrecs), namestr, self.SERVICE_TYPE, lout.provider, 
            provider_query=queries, record_format=Lifemapper.RECORD_FORMAT_MAP, 
            records=stdrecs, errors=errmsgs)
        return full_out

    # ...............................................
    def get_records(
            self, namestr, scenariocode, color, do_match, req_providers, 
            search_params=None):
        allrecs = []
        # for response metadata
        query_term = ''
        if namestr is not None:
            query_term = namestr
        elif search_params:
            query_term = 'invalid query term'
            
        for pr in req_providers:
            # Lifemapper
            if pr == ServiceProviderNew.Lifemapper[S2nKey.PARAM]:
                lmoutput = self._get_lifemapper_records(
                    namestr, scenariocode, color, do_match)
                allrecs.append(lmoutput)

        # Assemble
        provstr = ', '.join(req_providers)
        full_out = S2nOutput(
            len(allrecs), query_term, APIService.Map, provstr, records=allrecs)
        return full_out

    # ...............................................
    @cherrypy.tools.json_out()
    def GET(self, namestr=None, scenariocode=Lifemapper.OBSERVED_SCENARIO_CODE, 
            color=None, do_match=True, **kwargs):
        """Get one or more taxon records for a scientific name string from each
        available name service.
        
        Args:
            namestr: a scientific name
            gbif_parse: flag to indicate whether to first use the GBIF parser 
                to parse a scientific name into canonical name 
        Return:
            a dictionary with keys for each service queried.  Values contain 
            lmtrex.services.api.v1.S2nOutput object with records as a 
            list of dictionaries of Lifemapper records corresponding to 
            maps with URLs and their layers in the Lifemapper archive
        """
        # No search_params defined for Map service yet
        search_params = None
        try:
            usr_params = self._standardize_params(
                namestr=namestr, scenariocode=scenariocode, color=color, do_match=do_match)
            
            # What to query
            namestr = usr_params['namestr']
            # Who to query
            valid_providers = self.get_providers(search_params=search_params)
            req_providers = self.get_valid_requested_providers(
                usr_params['provider'], valid_providers)


            if namestr is None and search_params is None:
                output = self._show_online(providers=valid_providers)
            else:
                # common filters
                scenariocode = usr_params['scenariocode']
                color = usr_params['color'] 
                do_match = usr_params['do_match']
                # Query
                output = self.get_records(
                    namestr, namestr, scenariocode, color, do_match, req_providers, 
                    search_params=search_params)
        except Exception as e:
            output = self.get_failure(query_term=namestr, errors=[str(e)])
        return output.response

# # .............................................................................
# @cherrypy.expose
# class _MapSvc(_S2nService):
#     SERVICE_TYPE = APIService.Map
#     
# # .............................................................................
# @cherrypy.expose
# class MapLM(_MapSvc):
#     PROVIDER = ServiceProvider.Lifemapper
# 
#     # ...............................................
#     def get_map_layers(self, namestr, scenariocode, color, do_match):
#         # Lifemapper only uses GBIF Backbone Taxonomy accepted names
#         if do_match is False:
#             scinames = [namestr] 
#         else:
#             gan = NameSvc()
#             gout = gan.GET(
#                 namestr=namestr, gbif_accepted=True, do_count=False, do_parse=True)
#             good_names = gout['records']
#             # Lifemapper uses GBIF Backbone Taxonomy accepted names
#             # If none, try provided namestr
#             scinames = []        
#             if len(good_names) == 0:
#                 scinames.append(namestr)
#             else:
#                 for namerec in good_names:
#                     try:
#                         scinames.append(namerec['scientificName'])
#                     except Exception as e:
#                         print('No scientificName element in GBIF record {} for {}'
#                               .format(namerec, namestr))
#         # 2-step until LM returns full objects
#         stdrecs = []
#         errmsgs = []
#         queries = []
#         for sname in scinames:
#             # Step 1, get projections
#             lout = LifemapperAPI.find_map_layers_by_name(
#                 sname, prjscenariocode=scenariocode, color=color)
#             stdrecs.extend(lout.records)
#             errmsgs.extend(lout.errors)
#             queries.extend(lout.provider_query)
#         
#         full_out = S2nOutput(
#             len(stdrecs), namestr, self.SERVICE_TYPE, lout.provider, 
#             provider_query=queries, record_format=Lifemapper.RECORD_FORMAT_MAP, 
#             records=stdrecs, errors=errmsgs)
#         return full_out
# 
#     # ...............................................
#     @cherrypy.tools.json_out()
#     def GET(self, namestr=None, scenariocode=Lifemapper.OBSERVED_SCENARIO_CODE, 
#             color=None, do_match=True, **kwargs):
#         """Get GBIF taxon records for a scientific name string
#         
#         Args:
#             namestr: a scientific name
#             color: one of a defined set of color choices for projection display 
#             kwargs: additional keyword arguments - to be ignored
# 
#         Return:
#             lmtrex.services.api.v1.S2nOutput object with records as a 
#             list of dictionaries of Lifemapper records corresponding to 
#             maps with URLs and their layers in the Lifemapper archive
#             
#         Todo: 
#             fix color parameter in Lifemapper WMS service
#         """
#         try:
#             usr_params = self._standardize_params(
#                 namestr=namestr, scenariocode=scenariocode, color=color, 
#                 do_match=do_match)
#             namestr = usr_params['namestr']
#             if not namestr:
#                 output = self._show_online()
#             else:
#                 output = self.get_map_layers(
#                     namestr,  usr_params['scenariocode'], usr_params['color'], 
#                     usr_params['do_match'])
#         except Exception as e:
#             output = self.get_failure(query_term=namestr, errors=[str(e)])
#         return output.response
# 
# # .............................................................................
# @cherrypy.expose
# class MapBISON(_MapSvc):
#     """
#     Note: unfinished
#     """
#     PROVIDER = ServiceProvider.BISON
#     # ...............................................
#     def get_itis_taxon(self, namestr):
#         ioutput = ItisAPI.match_name(namestr)
#         return ioutput
# 
#     # ...............................................
#     @cherrypy.tools.json_out()
#     def GET(self, namestr=None, gbif_parse=True, **kwargs):
#         """Get ITIS accepted taxon records for a scientific name string
#         
#         Args:
#             namestr: a scientific name
#             gbif_parse: flag to indicate whether to first use the GBIF parser 
#                 to parse a scientific name into canonical name 
#             kwargs: additional keyword arguments - to be ignored
#  
#         Return:
#             lmtrex.services.api.v1.S2nOutput object with records as a 
#             list of dictionaries of BISON records corresponding to 
#             maps with URLs and their layers in the BISON database
#         """
#         try:
#             usr_params = self._standardize_params(
#                 namestr=namestr, gbif_parse=gbif_parse)
#             namestr = usr_params['namestr']
#             if not namestr:
#                 output = self._show_online()
#             else:
#                 output = self.get_itis_taxon(namestr)
#         except Exception as e:
#             output = self.get_failure(query_term=namestr, errors=[str(e)])
#         return output.response
# 
# # .............................................................................
# @cherrypy.expose
# class MapTentacles(_MapSvc):
#     PROVIDER = ServiceProvider.S2N
#     # ...............................................
#     def get_records(self, namestr, gbif_status, gbif_count ,status, kingdom):
#         allrecs = []
#         # Lifemapper
#         api = MapLM()
#         try:
#             lmoutput = api.get_gbif_matching_taxon(namestr, gbif_status, gbif_count)
#         except Exception as e:
#             return self.get_failure(query_term=namestr, errors=[str(e)])
#         else:
#             allrecs.append(lmoutput)
# 
#         full_out = S2nOutput(
#             len(allrecs), namestr, APIService.Map, self.PROVIDER[S2nKey.NAME], 
#             records=allrecs)
#         return full_out
# 
#     # ...............................................
#     @cherrypy.tools.json_out()
#     def GET(self, namestr=None, gbif_accepted=True, gbif_parse=True, 
#             gbif_count=True, status=None, kingdom=None, **kwargs):
#         """Get one or more taxon records for a scientific name string from each
#         available name service.
#         
#         Args:
#             namestr: a scientific name
#             gbif_parse: flag to indicate whether to first use the GBIF parser 
#                 to parse a scientific name into canonical name 
#         Return:
#             a dictionary with keys for each service queried.  Values contain 
#             lmtrex.services.api.v1.S2nOutput object with records as a 
#             list of dictionaries of Lifemapper records corresponding to 
#             maps with URLs and their layers in the Lifemapper archive
#         """
#         try:
#             usr_params = self._standardize_params(
#                 namestr=namestr, gbif_accepted=gbif_accepted, gbif_parse=gbif_parse, 
#                 gbif_count=gbif_count, status=status, kingdom=kingdom)
#             namestr = usr_params['namestr']
#             if not namestr:
#                 output = self._show_online()
#             else:
#                 output = self.get_records(
#                     namestr, usr_params['gbif_status'], usr_params['gbif_count'],
#                     usr_params['status'], usr_params['kingdom'])
#         except Exception as e:
#             output = self.get_failure(query_term=namestr, errors=[str(e)])
#         return output.response

# .............................................................................
if __name__ == '__main__':
    # test    
#     Phlox longifolia Nutt., 2927725
    names = TST_VALUES.NAMES[0:2]
#     names = ['Puntius ticto']
    for namestr in names:
        print('Name = {}'.format(namestr))
        
        lmapi = MapSvc()
        out = lmapi.GET(namestr=namestr)
        print_s2n_output(out)
