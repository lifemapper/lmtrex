import cherrypy
from http import HTTPStatus

from lmtrex.common.lmconstants import (APIService, ServiceProvider, TST_VALUES)
from lmtrex.common.s2n_type import (S2nKey, S2nOutput, S2nSchema, print_s2n_output)
from lmtrex.services.api.v1.base import _S2nService
from lmtrex.tools.provider.gbif import GbifAPI
from lmtrex.tools.provider.lifemapper import LifemapperAPI
from lmtrex.tools.utils import get_traceback, combine_errinfo, add_errinfo

# .............................................................................
@cherrypy.expose
@cherrypy.popargs('namestr')
class MapSvc(_S2nService):
    SERVICE_TYPE = APIService.Map
    ORDERED_FIELDNAMES = S2nSchema.get_s2n_fields(APIService.Map['endpoint'])
    
    # ...............................................
    def _match_gbif_names(self, namestr, is_accepted):
        scinames = []
        errinfo = {}
        try:
            # Get name from Gbif        
            nm_output = GbifAPI.match_name(namestr, is_accepted=is_accepted)
        except Exception as e:
            # emsg = 'Failed to match {} to GBIF accepted name'.format(namestr)
            traceback = get_traceback()
            errinfo = add_errinfo(errinfo, 'error', traceback)
            scinames.append(namestr)
        else:
            for rec in nm_output.records:
                try:
                    scinames.append(rec['s2n:scientific_name'])
                except Exception as e:
                    errinfo['warning'].append(
                        'No scientificName element in GBIF record {} for {}'.format(rec, namestr))
        return scinames, errinfo

    # ...............................................
    def _get_lifemapper_records(self, namestr, is_accepted, scenariocodes, color):
        errinfo = {}
        # First: get name(s)
        if is_accepted is False:
            scinames = [namestr] 
        else:
            scinames, errinfo = self._match_gbif_names(namestr, is_accepted=is_accepted)
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
                errinfo = add_errinfo(errinfo, 'error', traceback)
                    
            else:
                queries.extend(lout.provider_query)
                errinfo = combine_errinfo(errinfo, lout.errors)
                statii.append(lout.provider_status_code)
                # assemble all records, errors, statuses, queries for provider metadata element
                if len(lout.records) > 0:
                    stdrecs.extend(lout.records)
        prov_meta = LifemapperAPI._get_provider_response_elt(
            query_status=statii, query_urls=queries)
        # query_term = 'namestr={}&is_accepted={}&scenariocodes={}&color={}'.format(
        #     namestr, is_accepted, scenariocodes, color)
        full_out = S2nOutput(
            len(stdrecs), self.SERVICE_TYPE['endpoint'], prov_meta, 
            records=stdrecs, record_format=self.SERVICE_TYPE[S2nKey.RECORD_FORMAT], errors=errinfo)
        full_out.format_records(self.ORDERED_FIELDNAMES)
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
        prov_meta = self._get_s2n_provider_response_elt(query_term=query_term)
        # TODO: Figure out why errors are retained from query to query!!!  Resetting to {} works.
        full_out = S2nOutput(
            len(allrecs), self.SERVICE_TYPE['endpoint'], provider=prov_meta, 
            records=allrecs, errors={})
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
        else:   
            try:
                good_params, errinfo = self._standardize_params(
                    namestr=namestr, provider=provider, gbif_parse=gbif_parse, 
                    is_accepted=is_accepted, scenariocode=scenariocode, color=color)
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
                    try:
                        # Do Query!
                        output = self.get_records(
                            good_params['namestr'], good_params['provider'], good_params['is_accepted'], 
                            good_params['scenariocode'], good_params['color'])
                        
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
    names = TST_VALUES.NAMES[5:9]
    names = ['Eucosma raracana', 'Tulipa sylvestris', 'Phlox longifolia Nutt']
    # names.insert(0, None)
    svc = MapSvc()
    for namestr in names:
        for scodes in (None, 'worldclim-curr'):
            for prov in svc.get_providers():
                out = svc.GET(namestr=namestr, scenariocode=scodes)
                print_s2n_output(out, do_print_rec=True)

"""
http://broker-dev.spcoco.org/api/v1/map/?provider=lm&namestr=test
https://data.lifemapper.org/api/v2/ogc/data_24209?layers=occ_24209&service=wms&request=getmap&styles=&format=image%2Fpng&transparent=true&version=1.0&height=800&srs=EPSG%3A3857&width=800&layerLabel=Occurrence%20Points&bbox=0,0,20037508.342789244,20037508.34278071
"""