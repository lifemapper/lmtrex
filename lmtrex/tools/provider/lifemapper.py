from lmtrex.common.lmconstants import (APIService, Lifemapper, ServiceProvider)
from lmtrex.services.api.v1.s2n_type import S2nKey, S2nOutput
from lmtrex.tools.provider.api import APIQuery
from lmtrex.tools.utils import get_traceback

# .............................................................................
class LifemapperAPI(APIQuery):
    """Class to query Lifemapper portal APIs and return results"""
    PROVIDER = ServiceProvider.Lifemapper[S2nKey.NAME]
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
    def _standardize_proj_layer_record(cls, rec, prjscenariocodes=None, color=None):
        errmsgs = []
        stat = endpoint = sdm_layer_name = proj_url = None
        scen_code = scen_link = species_name = modtime = None
        try:
            stat = rec['status']
        except Exception as e:
            errmsgs.append(cls._get_error_message(
                msg='Failed to retrieve status element'))
        else:
            # No incomplete projection layer
            if stat != Lifemapper.COMPLETE_STAT_VAL:
                errmsgs.append(cls._get_error_message(
                    msg='SDM projection status is not complete'))
            else:
                try:
                    scen_code = rec['projectionScenario']['code']
                except Exception as e:
                    errmsgs.append(cls._get_error_message(
                        'Failed to retrieve projectionScenario/code element'))
                else:
                    # ignore
                    if prjscenariocodes and scen_code not in prjscenariocodes:
                        pass
                    # Return all valid projection layers or requested projection layer for scenario
                    else:
                        try:
                            mapname = rec['map']['mapName']
                            url = rec['map']['endpoint']
                            sdm_layer_name = rec['map']['layerName']
                            endpoint = '{}/{}'.format(url, mapname)
                        except Exception as e:
                            errmsgs.append(cls._get_error_message(
                                'Failed to retrieve map info {}'.format(e)))
                        else:
                            try:
                                data_url = rec['spatialRaster']['dataUrl']
                                proj_url = data_url.rstrip('/gtiff')
                            except:
                                errmsgs.append(cls._get_error_message(
                                    'Failed to retrieve spatialRaster/dataUrl element'))
                            try:
                                scen_link = rec['projectionScenario']['metadataUrl']
                            except Exception as e:
                                errmsgs.append(cls._get_error_message(
                                    'Failed to retrieve projectionScenario/metadataUrl element'))
                            try:
                                species_name = rec['speciesName']
                            except:
                                errmsgs.append(cls._get_error_message(
                                    'Failed to get speciesName element'))
                            try:
                                modtime = rec['statusModTime']
                            except:
                                errmsgs.append(cls._get_error_message(
                                    'Failed to get speciesName element'))
        newrec = {
            'endpoint': endpoint,
            'layer_type': 'raster',
            'layer_name': sdm_layer_name,
            'sdm_projection_link': proj_url,
            'sdm_projection_scenario_code': scen_code,
            'sdm_projection_scenario_link': scen_link,
            'species_name': species_name,
            'status': stat,
            'modtime': modtime,
            }
        # Ran the gauntlet of errors
        if color is not None and endpoint is not None:
            newrec['vendor-specific-parameters'] = {'color': color}
        newrec[S2nKey.ERRORS] = errmsgs
        return newrec
    
    # ...............................................
    @classmethod
    def _standardize_occ_layer_record(cls, rec, color=None):
        errmsgs = []
        stat = endpoint = point_url = point_layer_name = ptcount = bbox = None
        species_name = modtime = None
        # Check status first
        try:
            stat = rec['status']
            # No incomplete projection layer
            if stat != Lifemapper.COMPLETE_STAT_VAL:
                errmsgs.append(cls._get_error_message('Point status is not complete'))
        except Exception as e:
            errmsgs.append(cls._get_error_message(msg='Missing `status` element'))
        else:
            try:
                mapname = rec['map']['mapName']
                map_url = rec['map']['endpoint']
                point_layer_name = rec['map']['layerName']
                endpoint = '{}/{}'.format(map_url, mapname)
            except Exception as e:
                errmsgs.append(cls._get_error_message(
                    'Failed to retrieve map info from {}, {}'.format(rec, e)))
            else:
                try:
                    point_url = rec['url']
                except:
                    errmsgs.append(cls._get_error_message('Failed to get point URL'))
                try:
                    ptcount = rec['spatialVector']['numFeatures']
                except:
                    errmsgs.append(cls._get_error_message('Failed to get spatialVector/numFeatures'))
                try:
                    bbox = rec['spatialVector']['bbox']
                except:
                    errmsgs.append(cls._get_error_message('Failed to get spatialVector/bbox'))
                try:
                    species_name = rec['speciesName']
                except:
                    errmsgs.append(cls._get_error_message('Failed to get speciesName'))
                try:
                    modtime = rec['statusModTime']
                except:
                    errmsgs.append(cls._get_error_message('Failed to get speciesName'))
        newrec = {
            'endpoint': endpoint,
            'point_link': point_url,
            'layer_type': 'vector',
            'layer_name': point_layer_name,
            'point_count': ptcount,
            'point_bbox': bbox,
            'species_name': species_name,
            'status': stat,
            'modtime': modtime}
        
        newrec[S2nKey.ERRORS] = errmsgs
        return newrec


    # ...............................................
    @classmethod
    def _standardize_map_output(
            cls, output, query_term, service, prjscenariocodes=None, color=None, count_only=False, 
            provider_query=[], err=None):
        occ_layer_rec = None
        stdrecs = []
        errmsgs = []
        if err is not None:
            errmsgs.append(err)
        if err is not None:
            errmsgs.append(err)
        # Records
        if len(output) == 0:
            errmsgs.append(cls._get_error_message(
                'Failed to return any map layers for {}'.format(query_term)))
        else:
            try:
                occ_url = output[0]['occurrenceSet']['metadataUrl']
            except Exception as e:
                errmsgs.append(cls._get_error_message('Failed to return occurrence URL'))
            else:
                occ_rec = cls._get_occurrenceset_record(occ_url)
                occ_layer_rec = cls._standardize_occ_layer_record(occ_rec)
                if occ_layer_rec is not None and occ_layer_rec['endpoint'] is None:
                    errmsgs.extend(occ_layer_rec[S2nKey.ERRORS])
                    occ_layer_rec = None
        
        if occ_layer_rec is not None and not count_only:
            stdrecs.append(occ_layer_rec)
            for r in output:
                try:
                    r2 = cls._standardize_proj_layer_record(
                        r, prjscenariocodes=prjscenariocodes, color=color)
                    if r2['endpoint'] is not None:
                        stdrecs.append(r2)
                except Exception as e:
                    errmsgs.append(cls._get_error_message(err=e))
        
        # TODO: revisit record format for other map providers
        std_output = S2nOutput(
            len(stdrecs), query_term, service, cls.PROVIDER, provider_query=provider_query, 
            record_format=Lifemapper.RECORD_FORMAT_MAP, records=stdrecs, errors=errmsgs )

        return std_output
    
    # ...............................................
    @classmethod
    def _standardize_occ_output(cls, output, color=None, count_only=False, err=None):
        stdrecs = []
        errmsgs = []
        total = len(output)
        if err is not None:
            errmsgs.append(err)
        # Records]
        if not count_only:
            for r in output:
                try:
                    stdrecs.append(cls._standardize_occ_record(r, color=color))
                except Exception as e:
                    errmsgs.append(cls._get_error_message(err=e))
        
        # TODO: revisit record format for other map providers
        std_output = S2nOutput(
            count=total, record_format=Lifemapper.RECORD_FORMAT_OCC, 
            records=stdrecs, provider=cls.PROVIDER, errors=errmsgs, 
            provider_query=None, query_term=None, service=None)

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
            std_output = cls._standardize_map_output(
                api.output, name, APIService.Map, provider_query=[api.url], 
                prjscenariocodes=prjscenariocodes, color=color, count_only=False, 
                err=api.error)

        return std_output

    # ...............................................
    @classmethod
    def find_occurrencesets_by_name(cls, name, logger=None):
        """
        List occurrences for a given scientific name.  
        
        Args:
            name: a scientific name 'Accepted' according to the GBIF Backbone 
                Taxonomy
            logger: optional logger for info and error messages.  If None, 
                prints to stdout    
, 
        Note: 
            Lifemapper contains only 'Accepted' name froms the GBIF Backbone 
            Taxonomy and this method requires them for success.
        """
        other_filters = {Lifemapper.NAME_KEY: name, Lifemapper.ATOM_KEY: 0}
        api = LifemapperAPI(
            resource=Lifemapper.OCC_RESOURCE, other_filters=other_filters)
        try:
            api.query_by_get()
        except Exception as e:
            out = cls.get_failure(errors=[cls._get_error_message(err=e)])
        else:
            # Standardize output from provider response
            out = cls._standardize_occ_output(api.output, err=api.error)

        full_out = S2nOutput(
            count=out.count, record_format=out.record_format, 
            records=out.records, provider=cls.PROVIDER, errors=out.errors, 
            provider_query=[api.url], query_term=name, 
            service=APIService.Map)
        return full_out    
   

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
            out = cls.get_failure(errors=[cls._get_error_message(err=e)])
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
