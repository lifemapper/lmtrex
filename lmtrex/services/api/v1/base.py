import typing

from lmtrex.common.lmconstants import (
    APIService, Lifemapper, VALID_MAP_REQUESTS, ServiceProvider, BrokerParameters, 
    VALID_ICON_OPTIONS)
from lmtrex.tools.provider.gbif import GbifAPI
from lmtrex.tools.provider.itis import ItisAPI
from lmtrex.services.api.v1.s2n_type import S2nOutput, S2nKey

# .............................................................................
class _S2nService:
    """Base S-to-the-N service, handles parameter names and acceptable values"""
    # overridden by subclasses
    SERVICE_TYPE = None

    # ...............................................
    @classmethod
    def get_providers(cls, filter_params=None):
        """ Return a set of strings indicating all providers valid for this service. """
        provnames = set()
        # Ignore as-yet undefined filter_params
        for p in ServiceProvider.all():
            if cls.SERVICE_TYPE['endpoint'] in p[S2nKey.SERVICES]:
                provnames.add(p[S2nKey.PARAM])
        provnames = list(provnames)
        return provnames

    # ...............................................
    @classmethod
    def get_valid_providers(cls, filter_params=None):
        """ Return a set of strings indicating all providers valid for this service. """
        provnames = set()
        # Ignore as-yet undefined filter_params
        for p in ServiceProvider.all():
            if cls.SERVICE_TYPE['endpoint'] in p[S2nKey.SERVICES]:
                provnames.add(p[S2nKey.PARAM])
                
        provnames = list(provnames)
        return provnames

    # .............................................................................
    @classmethod
    def get_failure(
        cls, count: int = 0, record_format: str = '',
        records: typing.List[dict] = [], provider: str = '', 
        errors: typing.List[dict] = [], provider_query: typing.List[str] = [],
        query_term: str = '', service: str = '') -> S2nOutput:
        """Output format for all (soon) S^n services
        
        Args:
            count: number of records returned
            record_format: schema for the records returned
            records: list of records (dictionaries)
            provider: original data provider
            errors: list of info messages, warnings and errors (dictionaries)
            provider_query: list of queries (url strings)
            query_term: query term provided by the user, ex: name or id
            service: type of S^n services
            
        Return:
            lmtrex.services.api.v1.S2nOutput object
        """
        if not service: 
            service = cls.SERVICE_TYPE['endpoint']
        all_output = S2nOutput(
            count, query_term, service, provider, 
            provider_query=provider_query, record_format=record_format,  
            records=records, errors=errors)
        return all_output

    # .............................................................................
    @classmethod
    def get_valid_requested_providers(cls, standardized_providers, valid_providers):
        # Who to query
        req_providers = set(standardized_providers)
        valid_providers = set(valid_providers)
        
        if req_providers is None: 
            req_providers = valid_providers
        else:
            # Note invalid providers
            invalid_providers = req_providers.difference(valid_providers)
            # Only return valid requested providers
            valid_req_providers = valid_providers.intersection(req_providers)
            if len(valid_req_providers) == 0:
                valid_req_providers = valid_providers
        return valid_req_providers, invalid_providers

    # # .............................................................................
    # @classmethod
    # def get_valid_requested_providers_new(cls, requested_providers, valid_providers):
    #     invalid_providers = set()
    #     # valid_providers = cls.get_valid_providers(filter_params=filter_params)
    #
    #     if requested_providers is None: 
    #         valid_req_providers = valid_providers
    #     else:
    #         # Who to query
    #         req_providers = set([prov.lower() for prov in requested_providers])
    #         # Note invalid providers
    #         invalid_providers = req_providers.difference(valid_providers)
    #         valid_req_providers = valid_providers.intersection(req_providers)
    #         # No providers --> all providers
    #         if len(valid_req_providers) == 0:
    #             valid_req_providers = valid_providers
    #     return valid_req_providers, invalid_providers

    # .............................................................................
    @classmethod
    def endpoint(cls):
        endpoint =  '{}/{}'.format(APIService.Root['endpoint'], cls.SERVICE_TYPE['endpoint'])
        return endpoint

    # ...............................................
    def _set_default(self, param, default):
        if param is None:
            param = default
        return param
    
    # ...............................................
    def _show_online(self, providers):
        svc = self.SERVICE_TYPE['endpoint']
        info = {
            'info': 'S^n {} service is online.'.format(svc)}

        param_lst = []
        for p in self.SERVICE_TYPE['params']:
            pinfo = BrokerParameters[p].copy()
            pinfo['type'] = str(type(pinfo['type']))
            if p == 'provider':
                pinfo['options'] = list(providers)
            param_lst.append({p: pinfo})
        info['parameters'] = param_lst
        
        output = S2nOutput(0, '', svc, ','.join(providers), errors=[info])
        return output

    # ...............................................
    def parse_name_with_gbif(self, namestr):
        output = GbifAPI.parse_name(namestr)
        try:
            rec = output['record']
        except:
            # Default to original namestring if parsing fails
            pass
        else:
            success = rec['parsed']
            namestr = rec['canonicalName']
            
            if success:
                if namestr.startswith('? '):
                    namestr = rec['scientificName']
        return namestr

    # ...............................................
    def match_name_with_itis(self, namestr):
        output = ItisAPI.match_name(namestr, status='valid')
        try:
            namestr = output['records'][0]['nameWOInd']
        except:
            # Default to original namestring if match fails
            pass
        return namestr
        
    # ...............................................
    def _fix_type(self, provided_val, default_val):
        if provided_val is None:
            return None
        # all strings are lower case
        try:
            provided_val = provided_val.lower()
        except:
            pass
        
        # Find type from sequence of options
        if isinstance(default_val, list) or isinstance(default_val, tuple):
            if len(default_val) <= 1:
                raise Exception('Sequence of options must contain > 1 item')
            # Find type from other value in sequence containing None
            if default_val[0] is not None:
                default_val = default_val[0]
            else:
                default_val = default_val[1]

        # Convert int, str to boolean
        if isinstance(default_val, bool):                
            if provided_val in (0, '0', 'no', 'false'):
                return False
            else:
                return True
        elif isinstance(default_val, str):                
            usr_val = str(provided_val)
            
        # Failed conversions return default value
        elif isinstance(default_val, float):
            try:             
                usr_val = float(provided_val)
            except:
                usr_val = default_val
        elif isinstance(default_val, int):                
            try:             
                usr_val = int(provided_val)
            except:
                usr_val = default_val
                
        return usr_val

    # ...............................................
    def _fix_type_new(self, key, provided_val):
        """Correct parameter by 
            * casting to correct type 
            * if there are limited options, make sure it valid.
           If the parameter is invalid (type or value), return the default.
        """
        valid_options = None
        if provided_val is None:
            return None
        # all strings are lower case
        try:
            provided_val = provided_val.lower()
        except:
            pass
        
        default_val = BrokerParameters[key]['default']
        type_val = BrokerParameters[key]['type']
        # If restricted options, check
        try:
            options = BrokerParameters[key]['options']
        except:
            options = None
        else:
            # Invalid option returns default value
            if provided_val in options:
                usr_val = provided_val
            else:
                valid_options = options
                usr_val = default_val
            
        # Cast values to correct type. Failed conversions return default value
        if isinstance(type_val, str) and not options:
            usr_val = str(provided_val)

        elif isinstance(type_val, float):
            try:
                usr_val = float(provided_val)
            except:
                usr_val = default_val
                
        # Boolean also tests as int, so try boolean first
        elif isinstance(type_val, bool):                
            if provided_val in (0, '0', 'n', 'no', 'f', 'false'):
                usr_val = False
            elif provided_val in (1, '1', 'y', 'yes', 't', 'true'):
                usr_val = True
            else:
                valid_options = (True, False)
                usr_val = default_val                    

        elif isinstance(type_val, int):
            try:
                usr_val = int(provided_val)
            except:
                usr_val = default_val
                
        else:
            usr_val = provided_val
                
        return usr_val, valid_options

    # ...............................................
    def _get_def_val(self, default_val):
        # Sequences containing None have that as default value, or first value
        if isinstance(default_val, list) or isinstance(default_val, tuple):
            def_val = default_val[0]
        else:
            def_val = default_val
        return def_val

        
    # ...............................................
    def _process_params(self, kwarg_defaults, user_kwargs):
        """
        Modify all user provided key/value pairs to change keys to lower case, 
        and change values to the expected type (string, int, float, boolean).
        
        Args:
            kwarg_defaults: dictionary of 
                * keys containing valid keyword parameters for the current 
                    service. All must be lowercase.
                * values containing 
                    * the default value or 
                    * list of valid values (first is default), or
                    * tuple of 2 elements: None (default), and a value of the correct type 
            user_kwargs: dictionary of keywords and values sent by the user for 
                the current service.
                
        Note:
            A list of valid values for a keyword can include None as a default 
                if user-provided value is invalid
        """
        good_params = {}
        # Correct all parameter keys/values present
        for key, provided_val in user_kwargs.items():
            key = key.lower()
            try:
                default_val = kwarg_defaults[key]
            except:
                pass
            else:
                usr_val = self._fix_type(provided_val, default_val)
                if usr_val is not None:
                    good_params[key] = usr_val
                
        # Add missing defaults
        for dkey, dval in kwarg_defaults.items():
            if good_params[dkey] is None:
                good_params[dkey] = self._get_def_val(dval)
            
        return good_params

    # .............................................................................
    @classmethod
    def get_multivalue_options(cls, user_vals, valid_vals):
        "Default for parameters allowing multiple values is to return results for all options"
        valid_params = set()
        invalid_params = set()        
        
        for v in user_vals:
            if v in valid_vals:
                valid_params.add(v)
            else:
                invalid_params.add(v)

        if not valid_params: 
            valid_params = valid_vals
            
        return list(valid_params), list(invalid_params)

    # .............................................................................
    @classmethod
    def get_valid_requested_providers_new(cls, user_provider_string, valid_providers):
        # valid_requested_providers = set()
        # invalid_providers = set()
        user_provs = []
        
        if user_provider_string:
            user_provider_string = user_provider_string.lower()
            tmpprovs = user_provider_string.split(',')
            user_provs = set([tp.strip() for tp in tmpprovs])
            
        valid_requested_providers, invalid_providers = cls.get_multivalue_options(user_provs, valid_providers)
        #     for prov in user_provs:
        #         if prov in valid_providers:
        #             valid_requested_providers.add(prov)
        #         else:
        #             invalid_providers.add(prov)
        #
        # if not valid_requested_providers: 
        #     valid_requested_providers = valid_providers
            
        return valid_requested_providers, invalid_providers

    # ...............................................
    def _process_params_new(self, user_kwargs, valid_providers):
        """
        Modify all user provided key/value pairs to change keys to lower case, 
        and change values to the expected type (string, int, float, boolean).
        
        Args:
            user_kwargs: dictionary of keywords and values sent by the user for 
                the current service.
                
        Note:
            A list of valid values for a keyword can include None as a default 
                if user-provided value is invalid
                
        Todo:
            Do we need not_in_valid_options for error message?
        """
        good_params = {}
        option_errors = []
        
        # Allows None or comma-delimited list
        valid_requested_providers, invalid_providers = self.get_valid_requested_providers_new(
            user_kwargs['provider'], valid_providers)
        if invalid_providers:
            option_errors.append(
                {'error':
                 'Value(s) {} for parameter provider not in valid options {}'.format(
                     invalid_providers, valid_providers)})

        # Correct all parameter keys/values present
        for key in self.SERVICE_TYPE['params']:
            val = user_kwargs[key]
            # Add valid providers to parameters
            if key == 'provider':
                good_params[key] = valid_requested_providers
                good_params['valid_providers'] = valid_providers
                
            # Do not edit namestr, maintain capitalization
            elif key == 'namestr':
                good_params['namestr'] = val
                
            # Require one valid icon_status
            elif key == 'icon_status':
                valid_stat = BrokerParameters[key]['options']
                if val is None or val not in valid_stat:
                    option_errors.append(
                        {'error':
                         'Value {} for parameter icon_status not in valid options {}'.format(
                             val, valid_stat)})
                    
            elif val is not None:
                # Allows None or comma-delimited list
                if key == 'scenariocode':
                    usr_scens = []
                    valid_scens = BrokerParameters[key]['options']
                    tmpscens = val.split(',') 
                    for ts in tmpscens:
                        # scen = ts.lower().strip()
                        usr_scens.append(ts.lower().strip())
                    valid_requested_scens, invalid_scens = self.get_multivalue_options(usr_scens, valid_scens)
                    # Accept good options (or default/all)
                    good_params[key] = valid_requested_scens
                    # But include message for invalid options
                    if invalid_scens:
                        option_errors.append(
                            {'error':
                             'Value(s) {} for parameter scenariocode not in valid options {}'.format(
                                 invalid_scens, valid_scens)})
                # All other parameters have single value
                else:
                    usr_val, valid_options = self._fix_type_new(key, val)
                    # TODO: Do we need this option_errors to correct user?
                    if valid_options is not None and val not in valid_options:
                        option_errors.append(
                            {'error': 
                             'Value {} for parameter {} is not in valid options {}'.format(
                                 val, key, BrokerParameters[key]['options'])})
                        good_params[key] = None
                    else:
                        good_params[key] = usr_val
                
        # Add defaults for missing parameters
        for key in self.SERVICE_TYPE['params']:
            param_meta = BrokerParameters[key]
        # for dkey, param_meta in BrokerParameters.items():
            try:
                val = good_params[key]
            except:
                good_params[key] = param_meta['default']
            
        return good_params, option_errors

    # ...............................................
    def _standardize_params(
            self, valid_providers=None, provider=None, namestr=None, is_accepted=False, gbif_parse=False,  
            gbif_count=False, itis_match=False, kingdom=None, 
            occid=None, dataset_key=None, count_only=False, url=None,
            scenariocode=None, bbox=None, color=None, exceptions=None, height=None, 
            layers=None, request=None, frmat=None, srs=None, transparent=None, 
            width=None, do_match=True, icon_status=None):
        """Standardize the parameters for all Name Services into a dictionary 
        with all keys as standardized parameter names and values as 
        correctly-typed user values or defaults. 
        
        Note: 
            This function sets default values, but defaults may be changed for 
            a few subclasses that share parameters but have different defaults.  
            Change default with _set_default, prior to calling this method.
        
        Args:
            provider: string containing a comma delimited list of provider 
                codes indicating which providers to query.  If the string is not present
                or 'all', all providers of this service will be queried.
            is_accepted: flag to indicate whether to limit to 'valid' or 
                'accepted' taxa in the ITIS Taxonomy or GBIF Backbone Taxonomy
            gbif_parse: flag to indicate whether to first use the GBIF parser 
                to parse a scientific name into canonical name
            gbif_count: flag to indicate whether to count occurrences in 
                service provider for this taxon
            itis_match: flag to indicate whether to first use the ITIS solr 
                service to match a scientific name to an ITIS accepted name,
                used with BISON
            kingdom: filter for ITIS records from this kingdom
            occid: a Specify occurrence GUID, mapped to the 
                dwc:occurrenceId field
            dataset_key: a GBIF dataset GUID for returning a set of points, 
                used with GBIF
            count_only: flag indicating whether to return records
            url: direct URL to Specify occurrence, only used with for Specify
                queries
            scenariocode: A lifemapper code indicating the climate scenario used
                to calculate predicted presence of a species 
            bbox: A (min x, min y, max x, max y) tuple of bounding parameters
            color: The color (or color ramp) to use for the map
            exceptions: The format to report exceptions in
            height: The height (in pixels) of the returned map
            layers: A comma-delimited list of layer names
            request: The request operation name to perform
            frmat: The desired response format, query parameter is
                'format'
            sld: (todo) A URL referencing a StyledLayerDescriptor XML file which
                controls or enhances map layers and styling
            sld_body: (todo) A URL-encoded StyledLayerDescriptor XML document which
                controls or enhances map layers and styling
            srs: The spatial reference system for the map output.  'crs' for
                version 1.3.0.
            transparent: Boolean indicating if the background of the map should
                be transparent
            width: The width (in pixels) of the returned map
            do_match: Flag indicating whether to query GBIF for the 'accepted' 
                scientific name
            icon_status: string indicating which version of the icon to return, valid options are:
                active, inactive, hover 
        Return:
            a dictionary containing keys and properly formated values for the
                user specified parameters.
        """
        empty_str = ''
        if valid_providers is None:
            valid_providers = (None, empty_str)
        kwarg_defaults = {
            # Sequences denote value options, the first is the default, 
            #    other values are of the required type
            # For name services
            'provider': valid_providers,
            'is_accepted': False, 
            'gbif_parse': False, 
            'gbif_count': False, 
            'itis_match': False, 
            'kingdom': (None, empty_str),
            # For occurrence services
            'occid': (None, empty_str), 
            'dataset_key': (None, empty_str), 
            'count_only': False, 
            'url': (None, empty_str),
            'scenariocode': (None, empty_str),
            'bbox': '-180,-90,180,90', 
            'color': Lifemapper.VALID_COLORS,
            'exceptions': (None, empty_str), 
            'height': 300, 
            # VALID broker parameter options, must be list
            'layers': Lifemapper.VALID_MAPLAYER_TYPES,
            'request': VALID_MAP_REQUESTS, 
            'format': None, 
            'srs': 'epsg:4326', 
            'transparent': None, 
            'width': 600, 
            'icon_status': VALID_ICON_OPTIONS}
        user_kwargs = {
            'provider': provider,
            'is_accepted': is_accepted, 
            'gbif_parse': gbif_parse, 
            'gbif_count': gbif_count, 
            'itis_match': itis_match, 
            'kingdom': kingdom, 
            'occid': occid, 
            'dataset_key': dataset_key, 
            'count_only': count_only, 
            'url': url,
            'scenariocode': scenariocode,
            'bbox': bbox, 
            'color': color, 
            'exceptions': exceptions, 
            'height': height, 
            'layers': layers, 
            'request': request, 
            'format': frmat, 
            'srs': srs, 
            'transparent': transparent, 
            'width': width, 
            'icon_status': icon_status}
        
        usr_params, bad_params = self._process_params(kwarg_defaults, user_kwargs)
        # Do not edit namestr, maintain capitalization
        usr_params['namestr'] = namestr
        # Allow for None or comma-delimited list of providers
        provs = []
        if provider is not None:
            provs = []
            # Prepared params are lower case 
            tmpprovs = usr_params['provider'].split(',') 
            for tp in tmpprovs:
                prov = tp.strip()
                if ServiceProvider.is_valid_param(prov):
                    provs.append(prov)
        usr_params['provider'] = provs
        # Allow for None or comma-delimited list of scenarios
        scens = []
        if scenariocode is not None:
            # Prepared params are lower case 
            tmpscens = usr_params['scenariocode'].split(',') 
            for ts in tmpscens:
                scen = ts.strip()
                if scen in Lifemapper.valid_scenario_codes():
                    scens.append(scen)
        usr_params['scenariocode'] = scens
        # Remove 'gbif_parse' and itis_match flags
        gbif_parse = usr_params.pop('gbif_parse')
        itis_match = usr_params.pop('itis_match')
        # Replace namestr with GBIF-parsed namestr
        if namestr:
            if gbif_parse: 
                usr_params['namestr'] = self.parse_name_with_gbif(namestr)
            elif itis_match:
                usr_params['namestr'] = self.parse_name_with_gbif(namestr)
                
        return usr_params, bad_params

    # ...............................................
    def _standardize_params_new(
            self, provider=None, namestr=None, is_accepted=False, gbif_parse=False,  
            gbif_count=False, itis_match=False, kingdom=None, 
            occid=None, dataset_key=None, count_only=False, url=None,
            scenariocode=None, bbox=None, color=None, exceptions=None, height=None, 
            layers=None, request=None, frmat=None, srs=None, transparent=None, 
            width=None, do_match=True, icon_status=None, filter_params=None):
        """
        Return:
            a dictionary containing keys and properly formated values for the
                user specified parameters.
        Note: 
            filter_params is present to distinguish between providers for occ service by 
            occurrence_id or by dataset_id.
        """
        user_kwargs = {
            'provider': provider,
            'namestr': namestr,
            'is_accepted': is_accepted, 
            'gbif_parse': gbif_parse, 
            'gbif_count': gbif_count, 
            'itis_match': itis_match, 
            'kingdom': kingdom, 
            'occid': occid, 
            'dataset_key': dataset_key, 
            'count_only': count_only, 
            'url': url,
            'scenariocode': scenariocode,
            'bbox': bbox, 
            'color': color, 
            'exceptions': exceptions, 
            'height': height, 
            'layers': layers, 
            'request': request, 
            'format': frmat, 
            'srs': srs, 
            'transparent': transparent, 
            'width': width, 
            'icon_status': icon_status}
        
        valid_providers = self.get_valid_providers(filter_params=filter_params)
        usr_params, option_errors = self._process_params_new(user_kwargs, valid_providers)

        # Remove gbif_parse and itis_match flags
        gbif_parse = itis_match = False
        try:
            gbif_parse = usr_params.pop('gbif_parse')
        except:
            pass
        try:
            itis_match = usr_params.pop('itis_match')
        except:
            pass
        # Replace namestr with GBIF-parsed namestr
        if namestr and (gbif_parse or itis_match):
            usr_params['namestr'] = self.parse_name_with_gbif(namestr)
                
        return usr_params, option_errors

    # ..........................
    @staticmethod
    def OPTIONS():
        """Common options request for all services (needed for CORS)"""
        return

# .............................................................................
if __name__ == '__main__':
    kwarg_defaults = {
        'count_only': False,
        'width': 600,
        'height': 300,
        'type': [],
        }