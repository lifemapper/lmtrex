from lmtrex.common.lmconstants import (
    APIService, COMMUNITY_SCHEMA, Lifemapper, ServiceProvider, S2N_SCHEMA)
from lmtrex.services.api.v1.s2n_type import S2nKey, S2nOutput
from lmtrex.tools.provider.api import APIQuery
from lmtrex.tools.utils import get_traceback

# .............................................................................
class LifemapperAPI(APIQuery):
    """Class to query Lifemapper portal APIs and return results"""
    PROVIDER = ServiceProvider.Lifemapper[S2nKey.NAME]
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
        # Discard incomplete records
        try:
            stat = rec['status']
        except:
            return newrec
        else:
            if stat != Lifemapper.COMPLETE_STAT_VAL:
                return newrec
        # Discard records without map info
        try:
            melt = rec['map']
        except Exception:
            return newrec        
        try:
            mapname = melt['mapName']
            map_url = melt['endpoint']
            layer_name = melt['layerName']
        except Exception as e:
            return newrec

        # Success
        # Add icon url
        newrec['{}:icon_url'.format(
            COMMUNITY_SCHEMA.S2N['code'])] = cls.get_icon_url(ServiceProvider.Lifemapper[S2nKey.PARAM])
        newrec[cls.MAP_MAP['endpoint']] = '{}/{}'.format(map_url, mapname)
        newrec[cls.MAP_MAP['layer_name']] = layer_name
        newrec[cls.MAP_MAP['status']] = stat
        
        for fldname, val in rec.items():
            # Leave out fields without value
            if val:
                if fldname == 'projectionScenario':
                    try:
                        scen_code = val['code']
                    except Exception:
                        pass
                    else:
                        # Discard records that do not pass filter
                        if prjscenariocodes and scen_code not in prjscenariocodes:
                            return {}
                        # Success
                        newrec[cls.MAP_MAP['sdm_projection_scenario_code']] = scen_code          
                        try:
                            newrec[cls.MAP_MAP['sdm_projection_scenario_link']] = val['metadataUrl']
                        except:
                            pass
                    
                elif fldname == 'spatialRaster':
                    newrec[cls.MAP_MAP['layer_type']] = 'raster'
                    try:
                        data_url = val['dataUrl']
                    except:
                        pass
                    else:
                        newrec[cls.MAP_MAP['data_link']] = data_url.rstrip('/gtiff')  
                                              
                elif fldname == 'spatialVector':
                    newrec[cls.MAP_MAP['layer_type']] = 'vector'
                    try:
                        newrec[cls.MAP_MAP['point_bbox']] = val['bbox']
                    except:
                        pass
                    
                    try:
                        newrec[cls.MAP_MAP['point_count']] = val['numFeatures']
                    except:
                        pass

                elif fldname in ('speciesName', 'statusModTime'):
                    newfldname = cls.MAP_MAP[fldname]
                    newrec[newfldname] =  val                    

        if color is not None:
            newrec['vendor-specific-parameters'] = {'color': color}
        return newrec

    # ...............................................
    @classmethod
    def _standardize_map_output(
            cls, output, query_term, service, prjscenariocodes=None, color=None, count_only=False, 
            provider_query=[], err={}):
        occ_layer_rec = None
        stdrecs = []
        errmsgs = []
        if err:
            errmsgs.append(err)
        # Records
        if len(output) == 0:
            errmsgs.append({'error': cls._get_error_message(
                'Failed to return any map layers for {}'.format(query_term))})
        else:
            try:
                occ_url = output[0]['occurrenceSet']['metadataUrl']
            except Exception as e:
                errmsgs.append({'error': cls._get_error_message('Failed to return occurrence URL')})
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
                    errmsgs.append({'error': cls._get_error_message(err=e)})
        
        # TODO: revisit record format for other map providers
        prov_meta = cls._get_provider_response_elt(prov_query_urls=provider_query)
        std_output = S2nOutput(
            len(stdrecs), query_term, service, provider=prov_meta, records=stdrecs, errors=errmsgs )

        return std_output
    
    # ...............................................
    @classmethod
    def _standardize_occ_output(cls, output, color=None, count_only=False, err={}):
        stdrecs = []
        errmsgs = {}
        total = len(output)
        if err:
            errmsgs.append(err)
        # Records]
        if not count_only:
            for r in output:
                try:
                    stdrecs.append(cls._standardize_occ_record(r, color=color))
                except Exception as e:
                    errmsgs.append({'error': cls._get_error_message(err=e)})
        
        # TODO: revisit record format for other map providers
        prov_meta = cls._get_provider_response_elt()
        std_output = S2nOutput(
            count=total, record_format=Lifemapper.RECORD_FORMAT_OCC, 
            records=stdrecs, provider=prov_meta, errors=errmsgs)

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
        other_filters[Lifemapper.NAME_KEY] = name
        other_filters[Lifemapper.ATOM_KEY] = 0
        api = LifemapperAPI(
            resource=Lifemapper.PROJ_RESOURCE, other_filters=other_filters)
        
        try:
            api.query_by_get()
        except Exception as e:
            std_output = cls.get_failure(errors=[cls._get_error_message(err=e)])
        else:
            api_err = None
            if api.error:
                api_err = {'error': api.error}
            
            std_output = cls._standardize_map_output(
                api.output, name, APIService.Map['endpoint'], provider_query=[api.url], 
                prjscenariocodes=prjscenariocodes, color=color, count_only=False, 
                err=api_err)

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
        api = APIQuery(url)            
        try:
            api.query_by_get()
        except Exception as e:
            out = cls.get_failure(errors=[{'error': cls._get_error_message(err=e)}])
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
