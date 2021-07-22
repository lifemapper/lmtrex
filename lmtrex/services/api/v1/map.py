import cherrypy
from http import HTTPStatus

from lmtrex.common.lmconstants import (
    APIService, ServiceProvider, Lifemapper, TST_VALUES)
from lmtrex.services.api.v1.base import _S2nService
from lmtrex.services.api.v1.s2n_type import (S2nKey, S2nOutput, print_s2n_output)
from lmtrex.tools.provider.gbif import GbifAPI
from lmtrex.tools.provider.lifemapper import LifemapperAPI
from lmtrex.tools.utils import get_traceback

# .............................................................................
@cherrypy.expose
@cherrypy.popargs('namestr')
class MapSvc(_S2nService):
    SERVICE_TYPE = APIService.Map
    
    # ...............................................
    def _match_gbif_names(self, namestr, is_accepted):
        scinames = []
        errmsgs = []
        try:
            # Get name from Gbif        
            nm_output = GbifAPI.match_name(namestr, is_accepted=is_accepted)
        except Exception as e:
            errmsgs.append({'error': 'Failed to match {} to GBIF accepted name'.format(namestr)})
            traceback = get_traceback()
            errmsgs.append({'error': traceback})
            scinames.append(namestr)
        else:
            for rec in nm_output.records:
                try:
                    scinames.append(rec['s2n:scientific_name'])
                except Exception as e:
                    print('No scientificName element in GBIF record {} for {}'
                          .format(rec, namestr))
        return scinames, errmsgs

    # ...............................................
    def _get_lifemapper_records(self, namestr, is_accepted, scenariocodes, color):
        errmsgs = []
        # First: get name(s)
        if is_accepted is False:
            scinames = [namestr] 
        else:
            scinames, errmsgs = self._match_gbif_names(namestr, is_accepted=is_accepted)
        # Second: get completed Lifemapper projections (map layers)
        stdrecs = []
        statii = []
        queries = []
        for sname in scinames:
            # TODO: search on occurrenceset, then also pull projection layers
            try:
                lout = LifemapperAPI.find_map_layers_by_name(
                    sname, prjscenariocodes=scenariocodes, color=color)
            except Exception as e:
                traceback = get_traceback()
                errmsgs.append({'error': traceback})
            else:
                # assemble all records, errors, statuses, queries for provider metadata element
                if len(lout.records) > 0:
                    stdrecs.extend(lout.records)
                    errmsgs.extend(lout.errors)
                    statii.append(lout.provider_status_code)
                    queries.extend(lout.provider_query)
        prov_meta = LifemapperAPI._get_provider_response_elt(
            query_status=statii, query_urls=queries)
        query_term = 'namestr={}&is_accepted={}&scenariocodes={}&color={}'.format(
            namestr, is_accepted, scenariocodes, color)
        full_out = S2nOutput(
            len(stdrecs), query_term, self.SERVICE_TYPE['endpoint'], prov_meta, 
            records=stdrecs, record_format=self.SERVICE_TYPE[S2nKey.RECORD_FORMAT], errors=errmsgs)
        return full_out.response

    # ...............................................
    def get_records(
            self, namestr, req_providers, is_accepted, scenariocodes, color):
        allrecs = []
        # for response metadata
        query_term = ''
        if namestr is not None:
            sc = scenariocodes
            if scenariocodes:
                sc = ','.join(scenariocodes)
            query_term = 'namestr={}&provider={}&is_accepted={}&scenariocodes={}&color={}'.format(
                namestr, ','.join(req_providers), is_accepted, sc, color)
        provnames = []
        for pr in req_providers:
            # Lifemapper
            if pr == ServiceProvider.Lifemapper[S2nKey.PARAM]:
                lmoutput = self._get_lifemapper_records(
                    namestr, is_accepted, scenariocodes, color)
                allrecs.append(lmoutput)
                provnames.append(ServiceProvider.Lifemapper[S2nKey.NAME])
        # Assemble
        prov_meta = self._get_s2n_provider_response_elt()
        full_out = S2nOutput(
            len(allrecs), query_term, self.SERVICE_TYPE['endpoint'], provider=prov_meta, 
            records=allrecs)
        return full_out

    # ...............................................
    @cherrypy.tools.json_out()
    def GET(self, namestr=None, provider=None, gbif_parse=True, is_accepted=True, 
            scenariocode=None, color=None, **kwargs):
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
        error_description = None
        http_status = int(HTTPStatus.OK)
        
        valid_providers = self.get_valid_providers()
        if namestr is None:
            output = self._show_online(valid_providers)
        elif namestr.lower() in APIService.get_other_endpoints(self.SERVICE_TYPE):
            output = self._show_online(valid_providers)
        else:   
            try:
                good_params, option_errors, fatal_errors = self._standardize_params(
                    namestr=namestr, provider=provider, gbif_parse=gbif_parse, 
                    is_accepted=is_accepted, scenariocode=scenariocode, color=color)
                # Bad parameters
                if fatal_errors:
                    error_description = '; '.join(fatal_errors)                            
                    http_status = int(HTTPStatus.BAD_REQUEST)
            except Exception as e:
                http_status = int(HTTPStatus.INTERNAL_SERVER_ERROR)
                error_description = get_traceback()
            else:
                if http_status != HTTPStatus.BAD_REQUEST:
                    try:
                        # Do Query!
                        output = self.get_records(
                            good_params['namestr'], good_params['provider'], good_params['is_accepted'], 
                            good_params['scenariocode'], good_params['color'])
                        
                        # Add message on invalid parameters to output
                        for err in option_errors:
                            output.append_value(S2nKey.ERRORS, err)
                            
                    except Exception as e:
                        http_status = int(HTTPStatus.INTERNAL_SERVER_ERROR)
                        error_description = get_traceback()
        if http_status == HTTPStatus.OK:
            return output.response
        else:
            raise cherrypy.HTTPError(http_status, error_description)

# .............................................................................
if __name__ == '__main__':
    pass
#     names = TST_VALUES.NAMES[5:9]
#     names = ['Tulipa sylvestris']
# #     names = ['Plagioecia patina']
#     names = ['Phlox longifolia Nutt']
#     names.insert(0, None)
#     svc = MapSvc()
#     for namestr in names:
#         for scodes in (None, 'worldclim-curr'):
#             for prov in svc.get_providers():
#                 out = svc.GET(namestr=namestr, scenariocode=scodes, provider=prov)
#                 print_s2n_output(out, do_print_rec=True)

"""
http://broker-dev.spcoco.org/api/v1/map/?provider=lm&namestr=test

"""