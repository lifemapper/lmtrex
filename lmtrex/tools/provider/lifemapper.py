from http import HTTPStatus

from lmtrex.common.lmconstants import (
    APIService, COMMUNITY_SCHEMA, Lifemapper, ServiceProvider, S2N_SCHEMA)
from lmtrex.services.api.v1.s2n_type import S2nKey, S2nOutput
from lmtrex.tools.provider.api import APIQuery
from lmtrex.tools.utils import get_traceback, combine_errinfo, add_errinfo

# .............................................................................
class LifemapperAPI(APIQuery):
    """Class to query Lifemapper portal APIs and return results"""
    PROVIDER = ServiceProvider.Lifemapper
    MAP_MAP = S2N_SCHEMA.get_lifemapper_map_map()
    
    # ...............................................
    def __init__(
            self, resource=Lifemapper.PROJ_RESOURCE, ident=None, command=None,  
            other_filters={}, logger=None):
        """Constructor
        
        Args:
            resource: Lifemapper service to query
            ident: a Lifemapper database key for the specified resource.  If 
                ident is None, list using other_filters
            command: optional 'count' to query with other_filters
            other_filters: optional filters
            logger: optional logger for info and error messages.  If None, 
                prints to stdout    
        """
        url = '{}/{}'.format(Lifemapper.URL, resource)
        if ident is not None:
            url = '{}/{}'.format(url, ident)
            # do not send filters if retrieving a known object
            other_filters = {}
        elif command in Lifemapper.COMMANDS:
            url = '{}/{}'.format(url, command)
        APIQuery.__init__(self, url, other_filters=other_filters, logger=logger)
        
    # ...............................................
    @classmethod
    def _standardize_layer_record(cls, rec, prjscenariocodes=[], color=None):
        newrec = {}
        mapfld = 'map'
        
        mapnamefld = 'mapName'
        endptfld = 'endpoint'
        layerfld = 'layerName'
        statusfld = 'status'
        
        scencode_fld = 'sdm_projection_scenario_code'
        scenlink_fld = 'sdm_projection_scenario_link'
        
        # Required top level elements
        try:
            status = rec[statusfld]
            melt = rec[mapfld]
        except Exception:
            return {}
        else:
            # Required value
            if status != Lifemapper.COMPLETE_STAT_VAL:
                return {}
            # Required map level elements
            try:
                mapname = melt[mapnamefld]
                map_url = melt[endptfld]
                layer_name = melt[layerfld]
                endpoint = '{}/{}'.format(map_url, mapname)
            except Exception as e:
                return {}
            # Required value if present
            try:
                scen_code = rec['projectionScenario']['code']
                scen_link = rec['projectionScenario']['metadataUrl']
            except Exception:
                scen_code = scen_link = None
            else:
                # Discard records that do not pass filter
                if prjscenariocodes and scen_code not in prjscenariocodes:
                    return {}
                
        for stdfld, provfld in cls.MAP_MAP.items():
            try:
                val = rec[provfld]
            except:
                val = None

            if provfld == endptfld:
                newrec[stdfld] = endpoint
                
            elif provfld == layerfld:
                newrec[stdfld] = layer_name
                
            elif provfld == statusfld:
                newrec[stdfld] = status
            
            elif provfld == scencode_fld and scen_code:
                newrec[stdfld] = scen_code          

            elif provfld == scenlink_fld and scen_code:
                newrec[stdfld] = scen_link
                
            elif provfld == 'spatialRaster':
                newrec[cls.MAP_MAP['layer_type']] = 'raster'
                try:
                    data_url = val['dataUrl']
                except:
                    pass
                else:
                    newrec[cls.MAP_MAP['data_link']] = data_url.rstrip('/gtiff')  
                                          
            elif provfld == 'spatialVector':
                newrec[cls.MAP_MAP['layer_type']] = 'vector'
                try:
                    newrec[cls.MAP_MAP['point_bbox']] = val['bbox']
                except:
                    pass
                
                try:
                    newrec[cls.MAP_MAP['point_count']] = val['numFeatures']
                except:
                    pass

            elif provfld in ('speciesName', 'modtime'):
                newrec[stdfld] =  val                    

        if color is not None:
            newrec['vendor_specific_parameters'] = {'color': color}
        return newrec

    # ...............................................
    @classmethod
    def _standardize_map_output(
            cls, output, service, query_status=None, prjscenariocodes=None, color=None, count_only=False, 
            query_urls=[], errinfo={}):
        occ_layer_rec = None
        stdrecs = []
            
        # Records
        if len(output) > 0:
            try:
                occ_url = output[0]['occurrence_set']['metadata_url']
            except Exception as e:
                msg = cls._get_error_message('Failed to return occurrence URL')
                errinfo = add_errinfo(errinfo, 'error', msg)
            else:
                occ_rec = cls._get_occurrenceset_record(occ_url)
                occ_layer_rec = cls._standardize_layer_record(occ_rec)
        
        if occ_layer_rec and not count_only:
            stdrecs.append(occ_layer_rec)
            for r in output:
                try:
                    r2 = cls._standardize_layer_record(
                        r, prjscenariocodes=prjscenariocodes, color=color)
                    if r2:
                        stdrecs.append(r2)
                except Exception as e:
                    msg = cls._get_error_message(err=e)
                    errinfo = add_errinfo(errinfo, 'error', msg)
        
        # TODO: revisit record format for other map providers
        prov_meta = cls._get_provider_response_elt(query_status=query_status, query_urls=query_urls)
        std_output = S2nOutput(
            len(stdrecs), service, provider=prov_meta, records=stdrecs, errors=errinfo)

        return std_output
    
    # ...............................................
    @classmethod
    def _standardize_occ_output(
            cls, output, query_status=None, query_urls=[], color=None, count_only=False, errinfo={}):
        stdrecs = []
        total = len(output)
        # Records]
        if not count_only:
            for r in output:
                try:
                    stdrecs.append(cls._standardize_occ_record(r, color=color))
                except Exception as e:
                    msg = cls._get_error_message(err=e)
                    errinfo = add_errinfo(errinfo, 'error', msg)
        
        # TODO: revisit record format for other map providers
        prov_meta = cls._get_provider_response_elt(query_status=query_status, query_urls=query_urls)
        std_output = S2nOutput(
            count=total, record_format=Lifemapper.RECORD_FORMAT_OCC, records=stdrecs, 
            provider=prov_meta, errors=errinfo)

        return std_output

    # ...............................................
    @classmethod
    def find_map_layers_by_name(
            cls, name, prjscenariocodes=None, color=None, other_filters={}, 
            logger=None):
        """
        List projections for a given scientific name.  
        
        Args:
            name: a scientific name 'Accepted' according to the GBIF Backbone 
                Taxonomy
            prjscenariocodes: one or more Lifemapper codes indicating whether the 
                environmental data used for creating the projection is 
                observed, or modeled past or future.  Codes are in 
                LmREx.common.lmconstants Lifemapper.*_SCENARIO_CODE*. If the 
                code is None, return a map with only occurrence points
            color: a string indicating a valid color for displaying a predicted
                distribution map 
            logger: optional logger for info and error messages.  If None, 
                prints to stdout    

        Note: 
            Lifemapper contains only 'Accepted' name froms the GBIF Backbone 
            Taxonomy and this method requires them for success.
        """
        errinfo = {}
        other_filters[Lifemapper.NAME_KEY] = name
        other_filters[Lifemapper.ATOM_KEY] = 0
        api = LifemapperAPI(
            resource=Lifemapper.PROJ_RESOURCE, other_filters=other_filters)
        
        try:
            api.query_by_get()
        except Exception as e:
            tb = get_traceback()
            errinfo = add_errinfo(errinfo, 'error', cls._get_error_message(err=tb))
            
            std_output = cls.get_api_failure(
                APIService.Map['endpoint'], HTTPStatus.INTERNAL_SERVER_ERROR, errinfo=errinfo)
        else:
            errinfo = add_errinfo(errinfo, 'error', api.error)
            
            std_output = cls._standardize_map_output(
                api.output, APIService.Map['endpoint'], query_status=api.status_code, 
                query_urls=[api.url], prjscenariocodes=prjscenariocodes, color=color, 
                count_only=False, errinfo=errinfo)

        return std_output
   
    # ...............................................
    @classmethod
    def _get_occurrenceset_record(cls, url, logger=None):
        """
        Return occurrenceset for a given metadata url.  
        
        Args:
            id: a unique id for a Lifemapper occurrenceSet
            logger: optional logger for info and error messages.  If None, 
                prints to stdout    
        """
        rec = None
        errinfo = {}
        api = APIQuery(url)            
        try:
            api.query_by_get()
        except Exception as e:
            tb = get_traceback()
            errinfo = add_errinfo(errinfo, 'error', cls._get_error_message(err=tb))
            out = cls.get_api_failure(
                APIService.Name['endpoint'], HTTPStatus.INTERNAL_SERVER_ERROR, errinfo=errinfo)
        else:
            try:
                rec = api.output
            except:
                pass
        return rec

# .............................................................................
if __name__ == '__main__':
    # test

    namestr = 'Plagioecia patina (Lamarck, 1816)'
    occset = LifemapperAPI.find_occurrencesets_by_name(namestr)

"""
http://client.lifemapper.org/api/v2/sdmproject?displayname=Conibiosoma%20elongatum&projectionscenariocode=worldclim-curr
http://client.lifemapper.org/api/v2/occurrence?displayname=Conibiosoma%20elongatum
"""
