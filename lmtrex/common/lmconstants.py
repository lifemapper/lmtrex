from collections import OrderedDict
import os

from lmtrex.config.local_constants import APP_PATH, FQDN
from lmtrex.services.api.v1.s2n_type import S2nKey

# .............................................................................
# hierarchySoFarWRanks <class 'list'>: ['41107:$Kingdom:Plantae$Subkingdom:Viridiplantae$Infrakingdom:Streptophyta$Superdivision:Embryophyta$Division:Tracheophyta$Subdivision:Spermatophytina$Class:Magnoliopsida$Superorder:Lilianae$Order:Poales$Family:Poaceae$Genus:Poa$Species:Poa annua$']
# hierarchyTSN <class 'list'>: ['$202422$954898$846494$954900$846496$846504$18063$846542$846620$40351$41074$41107$']
# APP_PATH = '/opt/lifemapper'
CONFIG_DIR = 'config'
TEST_SPECIFY7_SERVER = 'http://preview.specifycloud.org'
TEST_SPECIFY7_RSS_URL = '{}/export/rss'.format(TEST_SPECIFY7_SERVER)

# Point to production or dev services depending on current location
if (FQDN.find('notyeti') >= 0 or FQDN.find('broker-dev') >= 0):
    ICON_API = 'https://broker-dev.spcoco.org/api/v1/badge'
    SPECIFY_CACHE_API = 'https://dev.syftorium.org/api/v1/sp_cache'
else:
    ICON_API = 'https://broker.spcoco.org/api/v1/badge'
    SPECIFY_CACHE_API = 'https://syftorium.org/api/v1/sp_cache'

# For saving Specify7 server URL (used to download individual records)
SPECIFY7_SERVER_KEY = 'specify7-server'
SPECIFY7_RECORD_ENDPOINT = 'export/record'
SPECIFY_ARK_PREFIX = 'http://spcoco.org/ark:/'

DATA_DUMP_DELIMITER = '\t'
GBIF_MISSING_KEY = 'unmatched_gbif_ids'

# VALID broker parameter options, must be list
VALID_MAP_REQUESTS = ['getmap', 'getlegendgraphic']
VALID_ICON_OPTIONS = ['active', 'inactive', 'hover']
ICON_DIR='lmtrex/static/img'

IMG_PATH = '/var/www'
ICON_CONTENT = 'image/png'
    
# .............................................................................
class DWC:
    QUALIFIER = 'dwc:'
    URL = 'http://rs.tdwg.org/dwc'
    SCHEMA = 'http://rs.tdwg.org/dwc.json'
    RECORD_TITLE = 'digital specimen object'

# .............................................................................
class DWCA:
    NS = '{http://rs.tdwg.org/dwc/text/}'
    META_FNAME = 'meta.xml'
    DATASET_META_FNAME = 'eml.xml'
    # Meta.xml element/attribute keys
    DELIMITER_KEY = 'fieldsTerminatedBy'
    LINE_DELIMITER_KEY = 'linesTerminatedBy'
    QUOTE_CHAR_KEY = 'fieldsEnclosedBy'
    LOCATION_KEY = 'location'
    UUID_KEY = 'id'
    FLDMAP_KEY = 'fieldname_index_map'
    FLDS_KEY = 'fieldnames'
    CORE_FIELDS_OF_INTEREST = [
        'id',
        'institutionCode',
        'collectionCode',
        'datasetName',
        'basisOfRecord',
        'year',
        'month',
        'day']
    # Human readable
    CORE_TYPE = '{}/terms/Occurrence'.format(DWC.URL)

JSON_HEADERS = {'Content-Type': 'application/json'}
CHERRYPY_CONFIG_FILE = os.path.join(APP_PATH, CONFIG_DIR, 'cherrypy.conf')


# .............................................................................
class TST_VALUES:
    SPECIFY_SOLR_COLLECTION = 'spcoco'
    KU_IPT_RSS_URL = 'http://ipt.nhm.ku.edu:8080/ipt/rss.do'
    ICH_RSS_URL = 'https://ichthyology.specify.ku.edu/export/rss'

    SPECIFY_RSS = 'https://ichthyology.specify.ku.edu/export/rss/'
    SPECIFY_URLS = [
    'https://ichthyology.specify.ku.edu/static/depository/export_feed/kui-dwca.zip',
    'https://ichthyology.specify.ku.edu/static/depository/export_feed/kuit-dwca.zip'
    ]

    DS_GUIDS_W_SPECIFY_ACCESS_RECS = [
        '56caf05f-1364-4f24-85f6-0c82520c2792', 
        '8f79c802-a58c-447f-99aa-1d6a0790825a']
    GUIDS_W_SPECIFY_ACCESS = [
        '2facc7a2-dd88-44af-b95a-733cc27527d4',
        '98fb49e0-591b-469e-99af-117b0bfdd7ee',
        '2c1becd5-e641-4e83-b3f5-76a55206539a', 
        'a413b456-0bff-47da-ab26-f074d9be5219',
        'dc92869c-1ed3-11e3-bfac-90b11c41863e',
        '21ac6644-5c55-44fd-b258-67eb66ea231d']
    GUIDS_WO_SPECIFY_ACCESS = [
        'ed8cfa5a-7b47-11e4-8ef3-782bcb9cd5b5',
        'f5725a56-7b47-11e4-8ef3-782bcb9cd5b5',
        'f69696a8-7b47-11e4-8ef3-782bcb9cd5b5',
        '5e7ec91c-4d20-42c4-ad98-8854800e82f7']
    DS_GUIDS_WO_SPECIFY_ACCESS_RECS = ['e635240a-3cb1-4d26-ab87-57d8c7afdfdb']
    BAD_GUIDS = [
        'KU :KUIZ:2200', 'KU :KUIZ:1663', 'KU :KUIZ:1569', 'KU :KUIZ:2462', 
        'KU :KUIZ:1743', 'KU :KUIZ:3019', 'KU :KUIZ:1816', 'KU :KUIZ:2542', 
        'KU :KUIZ:2396']
    NAMES = [
        'Plagioecia patina',
        'Plagiloecia patina Lamarck, 1816',
        'Plagioecia patina (Lamarck, 1816)',
        'Plagiloecia patana Lemarck',
        'Phlox longifolia Nutt.',
        'Tulipa sylvestris L.',
        'Medinilla speciosa Blume',
        'Acer caesium Wall. ex Brandis', 
        'Acer heldreichii Orph. ex Boiss.', 
        'Acer pseudoplatanus L.', 
        'Acer velutinum Boiss.', 
        'Acer hyrcanum Fisch. & Meyer', 
        'Acer monspessulanum L.', 
        'Acer obtusifolium Sibthorp & Smith', 
        'Acer opalus Miller', 
        'Acer sempervirens L.', 
        'Acer floridanum (Chapm.) Pax', 
        'Acer grandidentatum Torr. & Gray', 
        'Acer leucoderme Small', 
        'Acer nigrum Michx.f.', 
        'Acer skutchii Rehder', 
        'Acer saccharum Marshall']
    ITIS_TSNS = [526853, 183671, 182662, 566578]

# .............................................................................
class APIService:
    Root = {'endpoint': '/api/v1', 'params': None,
        S2nKey.RECORD_FORMAT: None}
    # Direct access to syftorium upload
    Address = {'endpoint': 'address', 'params': None,
        S2nKey.RECORD_FORMAT: 'url string'}
    # Icons for service providers
    Badge = {
        'endpoint': 'badge', 
        'params': ['provider', 'icon_status'],
        S2nKey.RECORD_FORMAT: 'image/png'}
    # Health for service providers
    Heartbeat = {'endpoint': 'heartbeat', 'params': None,
        S2nKey.RECORD_FORMAT: 'Broker heartbeat service schema TBD'}
    # Metadata for map services
    Map = {
        'endpoint': 'map', 
        'params': ['provider', 'namestr', 'gbif_parse', 'is_accepted', 'scenariocode', 'color'],
        S2nKey.RECORD_FORMAT: 'Broker map service schema TBD'}
    # Taxonomic Resolution
    Name = {
        'endpoint': 'name', 
        'params': ['provider', 'namestr', 'is_accepted', 'gbif_parse', 'gbif_count', 'kingdom'],
        S2nKey.RECORD_FORMAT: 'Broker name service schema TBD'}
    # Specimen occurrence records
    Occurrence = {'endpoint': 'occ', 'params': ['provider', 'occid', 'dataset_key', 'count_only'],
        S2nKey.RECORD_FORMAT: 'Broker occurrence service schema TBD'}
    # Specify guid resolver
    Resolve = {
        'endpoint': 'resolve', 
        'params': ['provider', 'occid'],
        S2nKey.RECORD_FORMAT: 'Broker GUID resolver service schema TBD'}
    # TODO: Consider an Extension service for Digital Object Architecture
    SpecimenExtension = {'endpoint': 'occext', 'params': None,
        S2nKey.RECORD_FORMAT: 'Broker specimen extension service schema TBD'}
    Frontend = {
        'endpoint': 'frontend',
        'params': ['occid', 'namestr'],
        S2nKey.RECORD_FORMAT: 'Broker frontend service schema TBD'}
    
    @classmethod
    def get_other_endpoints(cls, api_svc):
        if api_svc == APIService.Root:
            return [
                APIService.Address['endpoint'], APIService.Badge['endpoint'],
                APIService.Heartbeat['endpoint'], APIService.Map['endpoint'],
                APIService.Name['endpoint'], APIService.Occurrence['endpoint'],  
                APIService.Resolve['endpoint'], APIService.SpecimenExtension['endpoint']]
        elif api_svc == APIService.Address: 
            return [
                APIService.Root['endpoint'], APIService.Badge['endpoint'],
                APIService.Heartbeat['endpoint'], APIService.Map['endpoint'],
                APIService.Name['endpoint'], APIService.Occurrence['endpoint'],  
                APIService.Resolve['endpoint'], APIService.SpecimenExtension['endpoint']]
        elif api_svc == APIService.Badge: 
            return [
                APIService.Root['endpoint'], APIService.Address['endpoint'],
                APIService.Heartbeat['endpoint'], APIService.Map['endpoint'],
                APIService.Name['endpoint'], APIService.Occurrence['endpoint'],  
                APIService.Resolve['endpoint'], APIService.SpecimenExtension['endpoint']]
        elif api_svc == APIService.Heartbeat: 
            return [
                APIService.Root['endpoint'], APIService.Address['endpoint'],
                APIService.Badge['endpoint'], APIService.Map['endpoint'],
                APIService.Name['endpoint'], APIService.Occurrence['endpoint'],  
                APIService.Resolve['endpoint'], APIService.SpecimenExtension['endpoint']]
        elif api_svc == APIService.Map: 
            return [
                APIService.Root['endpoint'], APIService.Address['endpoint'],
                APIService.Badge['endpoint'], APIService.Heartbeat['endpoint'], 
                APIService.Name['endpoint'], APIService.Occurrence['endpoint'],  
                APIService.Resolve['endpoint'], APIService.SpecimenExtension['endpoint']]
        elif api_svc == APIService.Name: 
            return [
                APIService.Root['endpoint'], APIService.Address['endpoint'], 
                APIService.Badge['endpoint'], APIService.Heartbeat['endpoint'], 
                APIService.Map['endpoint'], APIService.Occurrence['endpoint'],  
                APIService.Resolve['endpoint'], APIService.SpecimenExtension['endpoint']]
        elif api_svc == APIService.Occurrence: 
            return [
                APIService.Root['endpoint'], APIService.Address['endpoint'], 
                APIService.Badge['endpoint'], APIService.Heartbeat['endpoint'], 
                APIService.Map['endpoint'], APIService.Name['endpoint'],   
                APIService.Resolve['endpoint'], APIService.SpecimenExtension['endpoint']]
        elif api_svc == APIService.SpecimenExtension: 
            return [
                APIService.Root['endpoint'], APIService.Address['endpoint'], 
                APIService.Badge['endpoint'], APIService.Heartbeat['endpoint'], 
                APIService.Map['endpoint'], APIService.Name['endpoint'], 
                APIService.Occurrence['endpoint'],  APIService.Resolve['endpoint']]
        elif api_svc == APIService.Resolve: 
            return [
                APIService.Root['endpoint'], APIService.Address['endpoint'], 
                APIService.Badge['endpoint'], APIService.Heartbeat['endpoint'], 
                APIService.Map['endpoint'], APIService.Name['endpoint'], 
                APIService.Occurrence['endpoint'], APIService.SpecimenExtension['endpoint']]
            

# .............................................................................
class ServiceProvider:
    GBIF = {
        S2nKey.NAME: 'GBIF', 
        S2nKey.PARAM: 'gbif', 
        S2nKey.SERVICES: [
            APIService.Occurrence['endpoint'], APIService.Name['endpoint'], APIService.Badge['endpoint']],
        'icon': {'active': '{}/gbif_active-01.png'.format(ICON_DIR),
                 'inactive': '{}/gbif_inactive-01.png'.format(ICON_DIR),
                 'hover': '{}/gbif_hover-01-01.png'.format(ICON_DIR)}
        }
    iDigBio = {
        S2nKey.NAME: 'iDigBio', 
        S2nKey.PARAM: 'idb', 
        S2nKey.SERVICES: [
            APIService.Occurrence['endpoint'], APIService.Badge['endpoint']],
        'icon': {'active': '{}/idigbio_colors_active-01.png'.format(ICON_DIR),
                 'inactive': '{}/idigbio_colors_inactive-01.png'.format(ICON_DIR),
                 'hover': '{}/idigbio_colors_hover-01.png'.format(ICON_DIR)}
        }
    # TODO: need an ITIS badge
    ITISSolr = {
        S2nKey.NAME: 'ITIS', 
        S2nKey.PARAM: 'itis', 
        S2nKey.SERVICES: [APIService.Badge['endpoint'], APIService.Name['endpoint']],
        'icon': {'active': '{}/itis_active.png'.format(ICON_DIR),
                 'inactive': '{}/itis_inactive.png'.format(ICON_DIR),
                 'hover': '{}/itis_hover.png'.format(ICON_DIR)}
        }
    Lifemapper = {
        S2nKey.NAME: 'Lifemapper', 
        S2nKey.PARAM: 'lm', 
        S2nKey.SERVICES: [
            APIService.Map['endpoint'], APIService.Badge['endpoint']],
        'icon': {'active': '{}/lm_active.png'.format(ICON_DIR),
                 'inactive': '{}/lm_inactive-01.png'.format(ICON_DIR),
                 'hover': '{}/lm_hover-01.png'.format(ICON_DIR)}
        }
    MorphoSource = {
        S2nKey.NAME: 'MorphoSource', 
        S2nKey.PARAM: 'mopho', 
        S2nKey.SERVICES: [
            APIService.Badge['endpoint'], APIService.Occurrence['endpoint'], 
            APIService.SpecimenExtension['endpoint']],
        'icon': {'active': '{}/morpho_active-01.png'.format(ICON_DIR),
                 'inactive': '{}/morpho_inactive-01.png'.format(ICON_DIR),
                 'hover': '{}/morpho_hover-01.png'.format(ICON_DIR)}
        }
    Specify = {
        S2nKey.NAME: 'Specify', 
        S2nKey.PARAM: 'specify', 
        S2nKey.SERVICES: [
            APIService.Badge['endpoint'], APIService.Occurrence['endpoint'], 
            APIService.Resolve['endpoint']],
        'icon': {'active': '{}/SpNetwork_active.png'.format(ICON_DIR),
                 'inactive': '{}/SpNetwork_inactive.png'.format(ICON_DIR),
                 'hover': '{}/SpNetwork_hover.png'.format(ICON_DIR)}}
    # TODO: need a Broker badge
    Broker = {
        S2nKey.NAME: 'Specify Network', 
        S2nKey.PARAM: 'specifynetwork', 
        S2nKey.SERVICES: []}
            # #APIService.Badge['endpoint'], 
            # APIService.Map['endpoint'], APIService.Name['endpoint'], 
            # APIService.Occurrence['endpoint'], APIService.Resolve['endpoint']]}
    # Syfter = {
    #     }
    
# ....................
    @classmethod
    def get_values(cls, param_or_name):
        if param_or_name in (
            ServiceProvider.GBIF[S2nKey.NAME], ServiceProvider.GBIF[S2nKey.PARAM]):
            return ServiceProvider.GBIF
        elif param_or_name in (
            ServiceProvider.iDigBio[S2nKey.NAME], ServiceProvider.iDigBio[S2nKey.PARAM]):
            return ServiceProvider.iDigBio
        elif param_or_name in (
            ServiceProvider.ITISSolr[S2nKey.NAME], ServiceProvider.ITISSolr[S2nKey.PARAM]):
            return ServiceProvider.ITISSolr
        elif param_or_name in (
            ServiceProvider.Lifemapper[S2nKey.NAME], ServiceProvider.Lifemapper[S2nKey.PARAM]):
            return ServiceProvider.Lifemapper
        elif param_or_name in (
            ServiceProvider.MorphoSource[S2nKey.NAME], ServiceProvider.MorphoSource[S2nKey.PARAM]):
            return ServiceProvider.MorphoSource
        elif param_or_name in (
            ServiceProvider.Specify[S2nKey.NAME], ServiceProvider.Specify[S2nKey.PARAM]):
            return ServiceProvider.Specify
        elif param_or_name in (
            ServiceProvider.Broker[S2nKey.NAME], ServiceProvider.Broker[S2nKey.PARAM]):
            return ServiceProvider.Broker
        else:
            return None
# ....................
    @classmethod
    def is_valid_param(cls, param):
        params = [svc[S2nKey.PARAM] for svc in cls.all()]
        if param in params:
            return True
        return False
# ....................
    @classmethod
    def is_valid_service(cls, param, svc):
        if param is not None:
            val_dict = ServiceProvider.get_values(param)
            if svc in (val_dict['services']):
                return True
        return False

# ....................
    @classmethod
    def get_name_from_param(cls, param):
        name = None
        if param is not None:
            val_dict = ServiceProvider.get_values(param)
            name = val_dict[S2nKey.NAME]
        return name

# ....................
    @classmethod
    def all(cls):
        return [
            ServiceProvider.GBIF, ServiceProvider.iDigBio, ServiceProvider.ITISSolr, 
            ServiceProvider.Lifemapper, ServiceProvider.MorphoSource, 
            ServiceProvider.Specify, ServiceProvider.Broker]

 # .............................................................................


# .............................................................................

URL_ESCAPES = [[" ", "\%20"], [",", "\%2C"]]
ENCODING = 'utf-8'


"""  
http://preview.specifycloud.org/static/depository/export_feed/kui-dwca.zip
http://preview.specifycloud.org/static/depository/export_feed/kuit-dwca.zip

curl '{}{}'.format(http://preview.specifycloud.org/export/record/
  | python -m json.tool

"""

# .............................................................................
# These fields must match the Solr core fields in spcoco/conf/schema.xml
SPCOCO_FIELDS = [
    # GUID and solr uniqueKey
    'id',
    # pull dataset/alternateIdentfier from DWCA eml.xml
    'dataset_guid',
    # ARK metadata
    # similar to DC Creator, Contributor, Publisher
    'who',
    # similar to DC Title
    'what',
    # similar to DC Date
    'when',
    # similar to DC Identifier, optional as this is the ARK
    'where',
    # Supplemental ARK metadata
    # redirection URL to specify7-server
    'url']

# ......................................................
class Lifemapper:
    URL = 'http://joe-124.lifemapper.org/api/v2'
    # URL = 'http://client.lifemapper.org/api/v2'
    OCC_RESOURCE = 'sdmproject'
    PROJ_RESOURCE = 'sdmproject'
    MAP_RESOURCE = 'ogc' 
    OBSERVED_SCENARIO_CODE = 'worldclim-curr'
    PAST_SCENARIO_CODES = ['CMIP5-CCSM4-lgm-10min', 'CMIP5-CCSM4-mid-10min']
    FUTURE_SCENARIO_CODES = [
        'AR5-CCSM4-RCP8.5-2050-10min', 'AR5-CCSM4-RCP4.5-2050-10min', 
        'AR5-CCSM4-RCP4.5-2070-10min', 'AR5-CCSM4-RCP8.5-2070-10min'] 
    OCC_RESOURCE = 'occurrence'
    OTHER_RESOURCES = ['taxonomy', 'scenario', 'envlayer']
    NAME_KEY = 'displayname'
    ATOM_KEY = 'atom'
    MIN_STAT_KEY ='after_status'
    MAX_STAT_KEY = 'before_status'
    COMPLETE_STAT_VAL = 300
    SCENARIO_KEY = 'projectionscenariocode'
    PROJECTION_METADATA_KEYS = [
        'modelScenario', 'projectionScenario', 'algorithm', 'spatialRaster']
    COMMANDS = ['count']
    # VALID broker parameter options must be list
    VALID_MAPLAYER_TYPES = ['occ', 'prj', 'bmng']
    VALID_MAP_FORMAT = ['image/png', 'image/gif', 'image/jpeg', 'image/tiff', 'image/x-aaigrid']
    VALID_SRS = ['epsg:4326', 'epsg:3857', 'AUTO:42003']
    VALID_COLORS = [
        'red', 'gray', 'green', 'blue', 'safe', 'pretty', 'yellow', 
        'fuschia', 'aqua', 'bluered', 'bluegreen', 'greenred']
    # TODO: replace with a schema definition
    RECORD_FORMAT_MAP = 'lifemapper_layer schema TBD'
    RECORD_FORMAT_OCC = 'lifemapper_occ schema TBD'
    
    @staticmethod
    def valid_scenario_codes():
        valid_scenario_codes = [Lifemapper.OBSERVED_SCENARIO_CODE]
        valid_scenario_codes.extend(Lifemapper.PAST_SCENARIO_CODES)
        valid_scenario_codes.extend(Lifemapper.FUTURE_SCENARIO_CODES)
        return valid_scenario_codes

BrokerParameters = {
    'provider': {
        'type': '', 'default': None, 'options': [
            ServiceProvider.GBIF[S2nKey.PARAM], ServiceProvider.iDigBio[S2nKey.PARAM],
            ServiceProvider.ITISSolr[S2nKey.PARAM], ServiceProvider.Lifemapper[S2nKey.PARAM], 
            ServiceProvider.MorphoSource[S2nKey.PARAM], ServiceProvider.Specify[S2nKey.PARAM]]
        },
    'namestr': {'type': '', 'default': None},
    'is_accepted': {'type': False, 'default': False},
    'gbif_parse': {'type': False, 'default': False},
    'gbif_count': {'type': False, 'default': False},
    'itis_match': {'type': False, 'default': False},
    'kingdom': {'type': '', 'default': None},
    'occid': {'type': '', 'default': None},
    'dataset_key': {'type': '', 'default': None},
    'count_only': {'type': False, 'default': False},
    'url': {'type': '', 'default': None},
    'scenariocode': {
        'type': '', 
        'options': Lifemapper.valid_scenario_codes(), 
        'default': None},
    'url': {'type': '', 'default': None},
    'bbox': {'type': '', 'default': '-180,-90,180,90'},
    'color': {
        'type': '', 
        'options': Lifemapper.VALID_COLORS, 
        'default': Lifemapper.VALID_COLORS[0]},
    'exceptions': {'type': '', 'default': None},
    'height': {'type': 300, 'default': 300},
    'width': {'type': 600, 'default': 600},
    'layers': {
        'type': '', 
        'options': Lifemapper.VALID_MAPLAYER_TYPES, 
        'default': Lifemapper.VALID_MAPLAYER_TYPES[0]},
    'request': {
        'type': '', 
        'options': VALID_MAP_REQUESTS, 
        'default': VALID_MAP_REQUESTS[0]},
    'format': {
        'type': '', 
        'options': Lifemapper.VALID_MAP_FORMAT,
        'default': Lifemapper.VALID_MAP_FORMAT[0]},
    'srs': {
        'type': '', 
        'options': Lifemapper.VALID_SRS,
        'default': Lifemapper.VALID_SRS[0]},
    'transparent': {'type': True, 'default': True},
    'icon_status': {
        'type': '', 
        'options': VALID_ICON_OPTIONS, 
        'default': None}
    }

# ......................................................
class MorphoSource:
    REST_URL = 'https://ms1.morphosource.org/api/v1'
    VIEW_URL = 'https://www.morphosource.org/concern/biological_specimens'
    NEW_VIEW_URL = 'https://www.morphosource.org/catalog/objects'
    NEW_API_URL = 'https://www.morphosource.org/catalog/objects.json'
    # FROZEN_URL = 'https://ea-boyerlab-morphosource-01.oit.duke.edu/api/v1'
    DWC_ID_FIELD = 'specimen.occurrence_id'
    LOCAL_ID_FIELD = 'specimen.specimen_id'
    OCC_RESOURCE = 'specimens'
    MEDIA_RESOURCE = 'media'
    OTHER_RESOURCES = ['taxonomy', 'projects', 'facilities']
    COMMAND = 'find'
    OCCURRENCEID_KEY = 'occurrence_id'
    TOTAL_KEY = 'totalResults'
    RECORDS_KEY = 'results'
    LIMIT = 1000
    RECORD_FORMAT = 'https://www.morphosource.org/About/API'

    @classmethod
    def get_occurrence_view(cls, local_id):
        """
        Example:
            https://www.morphosource.org/concern/biological_specimens/000S27385
        """
        url = None
        if local_id:
            idtail = 'S{}'.format(local_id)
            leading_zero_count = (9 - len(idtail))
            prefix = '0' * leading_zero_count
            url ='{}/{}{}'.format(MorphoSource.VIEW_URL, prefix, idtail)
        return url

    @classmethod
    def get_occurrence_data(cls, occurrence_id):
        url = None
        if occurrence_id:
            url = '{}/find/specimens?start=0&limit=1000&q=occurrence_id%3A{}'.format(
                MorphoSource.REST_URL, occurrence_id)
        return url
    
# ......................................................
class SPECIFY:
    """Specify constants enumeration
    """
    DATA_DUMP_DELIMITER = '\t'
    RECORD_FORMAT = 'http://rs.tdwg.org/dwc.json'
    RESOLVER_COLLECTION = 'spcoco'
    RESOLVER_LOCATION = 'notyeti-192.lifemapper.org'
    
# ......................................................
class SYFTER:
    REST_URL = 'https://syftorium.org/api/v1'
    REST_URL_DEV = 'https://dev.syftorium.org/api/v1'
    RESOLVE_RESOURCE = 'resolve'
    
    
# ......................................................
class GBIF:
    """GBIF constants enumeration"""
    DATA_DUMP_DELIMITER = '\t'
    TAXON_KEY = 'specieskey'
    TAXON_NAME = 'sciname'
    PROVIDER = 'puborgkey'
    OCC_ID_FIELD = 'gbifID'
    SPECIES_ID_FIELD = 'usageKey'
    WAIT_TIME = 180
    LIMIT = 300
    VIEW_URL = 'https://www.gbif.org'
    REST_URL = 'https://api.gbif.org/v1'
    QUALIFIER = 'gbif:'

    SPECIES_SERVICE = 'species'
    PARSER_SERVICE = 'parser/name'
    OCCURRENCE_SERVICE = 'occurrence'
    DATASET_SERVICE = 'dataset'
    ORGANIZATION_SERVICE = 'organization'
    
    COUNT_KEY = 'count'
    RECORDS_KEY = 'results'
    RECORD_FORMAT_NAME = 'https://www.gbif.org/developer/species'
    RECORD_FORMAT_OCCURRENCE = 'https://www.gbif.org/developer/occurrence'

    TAXONKEY_FIELD = 'specieskey'
    TAXONNAME_FIELD = 'sciname'
    PROVIDER_FIELD = 'puborgkey'
    ID_FIELD = 'gbifid'

    ACCEPTED_NAME_KEY = 'accepted_name'
    SEARCH_NAME_KEY = 'search_name'
    SPECIES_KEY_KEY = 'speciesKey'
    SPECIES_NAME_KEY = 'species'
    TAXON_ID_KEY = 'taxon_id'

    REQUEST_SIMPLE_QUERY_KEY = 'q'
    REQUEST_NAME_QUERY_KEY = 'name'
    REQUEST_TAXON_KEY = 'TAXON_KEY'
    REQUEST_RANK_KEY = 'rank'
    REQUEST_DATASET_KEY = 'dataset_key'

    DATASET_BACKBONE_VALUE = 'GBIF Backbone Taxonomy'
    DATASET_BACKBONE_KEY = 'd7dddbf4-2cf0-4f39-9b2a-bb099caae36c'

    SEARCH_COMMAND = 'search'
    COUNT_COMMAND = 'count'
    MATCH_COMMAND = 'match'
    DOWNLOAD_COMMAND = 'download'
    DOWNLOAD_REQUEST_COMMAND = 'request'
    RESPONSE_NOMATCH_VALUE = 'NONE'
    
    NameMatchFieldnames = [
        'scientificName', 'kingdom', 'phylum', 'class', 'order', 'family',
        'genus', 'species', 'rank', 'genusKey', 'speciesKey', 'usageKey',
        'canonicalName', 'confidence']

    # For writing files from GBIF DarwinCore download,
    # DWC translations in lmCompute/code/sdm/gbif/constants
    # We are adding the 2 fields: LM_WKT_FIELD and LINK_FIELD
    LINK_FIELD = 'gbifurl'
    # Ends in / to allow appending unique id
    
    @classmethod
    def species_url(cls):
        return '{}/{}'.format(GBIF.VIEW_URL, GBIF.SPECIES_SERVICE)
    
    @classmethod
    def get_occurrence_view(cls, key):
        url = None
        if key:
            url = '{}/{}/{}'.format(GBIF.VIEW_URL, GBIF.OCCURRENCE_SERVICE, key)
        return url

    @classmethod
    def get_occurrence_data(cls, key):
        url = None
        if key:
            url = '{}/{}/{}'.format(GBIF.REST_URL, GBIF.OCCURRENCE_SERVICE, key)
        return url

    @classmethod
    def get_species_view(cls, key):
        url = None
        if key:
            url = '{}/{}/{}'.format(GBIF.VIEW_URL, GBIF.SPECIES_SERVICE, key)
        return url

    @classmethod
    def get_species_data(cls, key):
        url = None
        if key:
            url = '{}/{}/{}'.format(GBIF.REST_URL, GBIF.SPECIES_SERVICE, key)
        return url


# .............................................................................
class COMMUNITY_SCHEMA:
    DWC = {'code': 'dwc', 'url': 'http://rs.tdwg.org/dwc/terms'}
    GBIF = {'code': 'gbif', 'url': 'https://gbif.github.io/dwc-api/apidocs/org/gbif/dwc/terms/GbifTerm.html'}
    DCT = {'code': 'dcterms', 'url': 'http://purl.org/dc/terms'}
    IDB = {'code': 'idigbio', 'url': ''}
    MS = {'code': 'mopho', 'url': 'https://www.morphosource.org/About/API'}
    S2N = {'code': 's2n', 'url': ''}

# .............................................................................
class S2N_SCHEMA:
    """
    Note: 
        All field values are strings unless otherwise indicated
    """
    NAME = OrderedDict({
        # Provider's URLs to this record in dictionary
        # 'provider_links': COMMUNITY_SCHEMA.S2N,
        'view_url': COMMUNITY_SCHEMA.S2N,
        'api_url': COMMUNITY_SCHEMA.S2N,
        # S2n standardization of common elements
        'status': COMMUNITY_SCHEMA.S2N,
        'scientific_name': COMMUNITY_SCHEMA.S2N,
        'canonical_name': COMMUNITY_SCHEMA.S2N,
        'common_names': COMMUNITY_SCHEMA.S2N,
        'kingdom': COMMUNITY_SCHEMA.S2N,
        'rank': COMMUNITY_SCHEMA.S2N,
        'synonyms': COMMUNITY_SCHEMA.S2N,           # list of strings
        'hierarchy': COMMUNITY_SCHEMA.S2N,     # list of (one) dictionary containing rank: name

        # Occurrence data for this name
        S2nKey.OCCURRENCE_COUNT: COMMUNITY_SCHEMA.S2N,
        S2nKey.OCCURRENCE_URL: COMMUNITY_SCHEMA.S2N,
        
        # GBIF-specific fields
        'gbif_confidence': COMMUNITY_SCHEMA.S2N,
        'gbif_taxon_key': COMMUNITY_SCHEMA.S2N,
        
        # ITIS-specific fields
        'itis_tsn': COMMUNITY_SCHEMA.S2N,
        'itis_credibility': COMMUNITY_SCHEMA.S2N,
        })
    MAP = OrderedDict({
        # Provider's URLs to this record in dictionary
        # 'provider_links': COMMUNITY_SCHEMA.S2N,
        'view_url': COMMUNITY_SCHEMA.S2N,
        'api_url': COMMUNITY_SCHEMA.S2N,

        'endpoint': COMMUNITY_SCHEMA.S2N,
        'data_link': COMMUNITY_SCHEMA.S2N,
        'sdm_projection_scenario_code': COMMUNITY_SCHEMA.S2N,
        'sdm_projection_scenario_link': COMMUNITY_SCHEMA.S2N,
        'layer_type': COMMUNITY_SCHEMA.S2N,
        'layer_name': COMMUNITY_SCHEMA.S2N,
        'point_count': COMMUNITY_SCHEMA.S2N,        # integer
        'point_bbox': COMMUNITY_SCHEMA.S2N,         # list of 4 float values: minX, minY, maxX, maxY
        'species_name': COMMUNITY_SCHEMA.S2N,
        'status': COMMUNITY_SCHEMA.S2N,             # integer
        'modtime': COMMUNITY_SCHEMA.S2N,
        # Lifemapper allows query_parameter 'color' with options:
        #    for Vector: RGB values as hexidecimal string #RRGGBB
        #    for Raster: gray, red, green, blue, yellow, fuschia, aqua, bluered, bluegreen, greenred
        'vendor_specific_parameters': COMMUNITY_SCHEMA.S2N,     # dictionary with queryparameter/value
        })
    OCCURRENCE = OrderedDict({
        # Provider's URLs to this record in dictionary
        # 'provider_links': COMMUNITY_SCHEMA.S2N,
        'view_url': COMMUNITY_SCHEMA.S2N,
        'api_url': COMMUNITY_SCHEMA.S2N,

        'accessRights': COMMUNITY_SCHEMA.DCT,
        'language': COMMUNITY_SCHEMA.DCT,
        'license': COMMUNITY_SCHEMA.DCT,
        'modified': COMMUNITY_SCHEMA.DCT,
        'type': COMMUNITY_SCHEMA.DCT,
        
        # # Dictionary of contents
        # 'taxon': COMMUNITY_SCHEMA.S2N,     # dictionary of taxonomic elements 
        'taxonRank': COMMUNITY_SCHEMA.DWC,
        'kingdom': COMMUNITY_SCHEMA.DWC,
        'phylum': COMMUNITY_SCHEMA.DWC,
        'class': COMMUNITY_SCHEMA.DWC,
        'order': COMMUNITY_SCHEMA.DWC,
        'family': COMMUNITY_SCHEMA.DWC,
        'genus': COMMUNITY_SCHEMA.DWC,
        'scientificName': COMMUNITY_SCHEMA.DWC,
        'specificEpithet': COMMUNITY_SCHEMA.DWC, 
        'scientificNameAuthorship': COMMUNITY_SCHEMA.DWC,
    
        'recordedBy': COMMUNITY_SCHEMA.DWC,
        'fieldNumber': COMMUNITY_SCHEMA.DWC,
        'occurrenceID': COMMUNITY_SCHEMA.DWC, 
        'institutionCode': COMMUNITY_SCHEMA.DWC,
        'collectionCode': COMMUNITY_SCHEMA.DWC,
        'catalogNumber': COMMUNITY_SCHEMA.DWC,
        'basisOfRecord': COMMUNITY_SCHEMA.DWC,
        'preparations': COMMUNITY_SCHEMA.DWC,
        'datasetName': COMMUNITY_SCHEMA.DWC,
    
        'associatedReferences': COMMUNITY_SCHEMA.DWC,       # list of strings 
        'associatedSequences': COMMUNITY_SCHEMA.DWC,        # list of strings
        'otherCatalogNumbers': COMMUNITY_SCHEMA.DWC,        # list of strings
        
        'locality': COMMUNITY_SCHEMA.DWC,
        'decimalLongitude': COMMUNITY_SCHEMA.DWC,
        'decimalLatitude': COMMUNITY_SCHEMA.DWC,
        'geodeticDatum': COMMUNITY_SCHEMA.DWC,
        'year': COMMUNITY_SCHEMA.DWC,
        'month': COMMUNITY_SCHEMA.DWC,
        'day': COMMUNITY_SCHEMA.DWC,
        
        # S2n resolution of non-standard contents
        'issues': COMMUNITY_SCHEMA.S2N,               # dictionary of codes: descriptions

        # GBIF-specific field
        'gbifID': COMMUNITY_SCHEMA.GBIF,
        'publishingOrgKey': COMMUNITY_SCHEMA.GBIF,
        'acceptedScientificName': COMMUNITY_SCHEMA.GBIF,

        # iDigBio-specific field
        'uuid': COMMUNITY_SCHEMA.IDB,
        
        # MorphoSource-specific field
        'specimen.specimen_id': COMMUNITY_SCHEMA.MS,

        # Specify7-specific field
        'specify_identifier': COMMUNITY_SCHEMA.S2N,
    })
    
    RESOLVED = OrderedDict({
        'ident': COMMUNITY_SCHEMA.S2N,
        'dataset_guid': COMMUNITY_SCHEMA.S2N,
        'institutionCode': COMMUNITY_SCHEMA.DWC,
        'basisOfRecord': COMMUNITY_SCHEMA.DWC,
        'date': COMMUNITY_SCHEMA.S2N,
        'ark': COMMUNITY_SCHEMA.S2N,
        'api_url': COMMUNITY_SCHEMA.S2N
    })
    
    RANKS = ('kingdom', 'phylum', 'class', 'order', 'family', 'genus', 'species')
    
    @classmethod
    def get_s2n_fields(cls, svc):
        if svc == APIService.Map['endpoint']:
            schema = S2N_SCHEMA.MAP
        elif svc == APIService.Name['endpoint']:
            schema = S2N_SCHEMA.NAME
        elif svc == APIService.Occurrence['endpoint']:
            schema = S2N_SCHEMA.OCCURRENCE
        elif svc == APIService.Resolve['endpoint']:
            schema = S2N_SCHEMA.RESOLVED
        else:
            schema = None
            
        flds = []
        try:
            for fname, ns in schema.items():
                flds.append('{}:{}'.format(ns, fname))
        except:
            pass
        return flds

    @classmethod
    def get_gbif_taxonkey_fld(cls):
        return '{}:gbif_taxon_key'.format(COMMUNITY_SCHEMA.S2N['code'])
    
    @classmethod
    def get_gbif_occcount_fld(cls):
        return '{}:{}'.format(COMMUNITY_SCHEMA.S2N['code'], S2nKey.OCCURRENCE_COUNT)
    
    @classmethod
    def get_gbif_occurl_fld(cls):
        return '{}:{}'.format(COMMUNITY_SCHEMA.S2N['code'], S2nKey.OCCURRENCE_URL)
    
    @classmethod
    def get_s2n_occurrence_fields(cls):
        stdnames = []
        for fn, comschem in S2N_SCHEMA.OCCURRENCE.items():
            stdnames.append('{}:{}'.format(comschem['code'], fn))
        return stdnames

    @classmethod
    def get_gbif_occurrence_map(cls):
        "Map GBIF  response fields to broker response fields"
        stdfld_provfld = OrderedDict()
        for fn, comschem in S2N_SCHEMA.OCCURRENCE.items():
            std_name = '{}:{}'.format(comschem['code'], fn)
            stdfld_provfld[std_name] = fn
        return stdfld_provfld

    @classmethod
    def get_idb_occurrence_map(cls):
        "Map iDigBio response fields to broker response fields"
        stdfld_provfld = OrderedDict()
        for fn, comschem in S2N_SCHEMA.OCCURRENCE.items():
            stdname = '{}:{}'.format(comschem['code'], fn)
            if fn == 'uuid':
                stdfld_provfld[stdname] = fn
            else:
                stdfld_provfld[stdname] = stdname
        return stdfld_provfld

    @classmethod
    def get_specify_occurrence_map(cls):
        "Map Specify response fields to broker response fields"
        # sname_stdname = {}
        stdfld_provfld = OrderedDict()
        for fn, comschem in S2N_SCHEMA.OCCURRENCE.items():
            spfldname = '{}/{}'.format(comschem['url'], fn)
            stdname = '{}:{}'.format(comschem['code'], fn)
            stdfld_provfld[stdname] = spfldname
        return stdfld_provfld
    
    @classmethod
    def get_specifycache_occurrence_map(cls):
        "Map Specify Cache response fields to broker response fields"
        stdfld_provfld = OrderedDict()
        names_in_spcache = [
            'accessRights','basisOfRecord','catalogNumber','class','collectionCode', 
            'datasetName', 'family','genus','geodeticDatum','identifier','institutionCode',
            'kingdom','locality','occurrenceID','order','phylum','recordedBy','scientificName']
        # Add urls
        names_in_spcache.extend(['api_url', 'view_url'])
        old_id = 'identifier' 
        new_id = 'specify_identifier'
        
        for fn, comschem in S2N_SCHEMA.OCCURRENCE.items():
            if fn in names_in_spcache:
                stdname = '{}:{}'.format(comschem['code'], fn)
                if fn == new_id:
                    stdfld_provfld[stdname] = old_id
                else:
                    stdfld_provfld[stdname] = fn
                
        return stdfld_provfld

    @classmethod
    def get_mopho_occurrence_map(cls):
        # mopho_stdname = {}
        stdfld_provfld = OrderedDict()
        for fn, comschem in S2N_SCHEMA.OCCURRENCE.items():
            std_name = '{}:{}'.format(comschem['code'], fn)
            if fn == 'catalogNumber':
                stdfld_provfld[std_name] = 'specimen.catalog_number'
            elif fn == 'institutionCode':
                stdfld_provfld[std_name] = 'specimen.institution_code'
            elif fn == 'occurrenceID':
                stdfld_provfld[std_name] = 'specimen.occurrence_id' 
            elif fn == 'uuid':
                stdfld_provfld[std_name] = 'specimen.uuid'
            elif fn in ['specimen.specimen_id', 'view_url', 'api_url']:
                stdfld_provfld[std_name] = fn
        return stdfld_provfld
    
    @classmethod
    def get_gbif_name_map(cls):
        "Map GBIF name response fields to broker response fields"
        stdfld_provfld = OrderedDict()
        for fn, comschem in S2N_SCHEMA.OCCURRENCE.items():
            std_name = '{}:{}'.format(comschem['code'], fn)
            if fn == 'scientific_name':
                oldname == 'scientificName':
            elif fn == 'canonical_name':
                oldname = 'canonicalName'
            elif fn == 'gbif_confidence':
                oldname = 'confidence'
            elif fn == 'gbif_taxon_key':
                oldname = 'usageKey'
            elif fn.startswith('itis'):
                oldname = None
            else:
                oldname = fn
            if oldname:
                stdfld_provfld[std_name] = oldname
        return stdfld_provfld

    @classmethod
    def get_itis_name_map(cls):
        "Map ITIS response fields to broker response fields"
        stdfld_provfld = OrderedDict()
        for fn, comschem in S2N_SCHEMA.OCCURRENCE.items():
            std_name = '{}:{}'.format(comschem['code'], fn)
            if fn == 'scientific_name':
                oldname == 'nameWTaxonAuthor':
            elif fn == 'canonical_name':
                oldname = 'nameWOInd'
            elif fn == 'hierarchy':
                oldname = 'hierarchySoFarWRanks'
            elif fn == 'status':
                oldname = 'usage'
            elif fn == 'itis_tsn':
                oldname = 'tsn'
            elif fn == 'itis_credibility':
                oldname = 'credibilityRating'
            elif fn.startswith('gbif'):
                oldname = None
            else:
                oldname = fn
            if oldname:
                stdfld_provfld[std_name] = oldname
        return stdfld_provfld
    
    @classmethod
    def get_lifemapper_map_map(cls):
        "Map Lifemapper response fields to broker response fields"
        stdfld_provfld = OrderedDict()
        for fn, comschem in S2N_SCHEMA.MAP.items():
            std_name = '{}:{}'.format(comschem['code'], fn)
            if fn == 'species_name':
                stdfld_provfld[std_name] = 'speciesName'
            elif fn == 'lm_status_code':
                stdfld_provfld[std_name] = 'status'
            elif fn == 'modtime':
                stdfld_provfld[std_name] = 'modtime'
            else:
                stdfld_provfld[std_name] = fn
        return stdfld_provfld

    @classmethod
    def get_specify_resolver_map(cls):
        "Map Specify Resolver response fields to broker response fields"
        stdfld_provfld = OrderedDict()
        for fn, comschem in S2N_SCHEMA.RESOLVED.items():
            std_name = '{}:{}'.format(comschem['code'], fn)
            if fn == 'ident':
                stdfld_provfld[std_name] = 'id'
            elif fn == 'institutionCode':
                stdfld_provfld[std_name] = 'who'
            elif fn == 'basisOfRecord':
                stdfld_provfld[std_name] = 'what'
            elif fn == 'date':
                stdfld_provfld[std_name] = 'when'
            elif fn == 'ark':
                stdfld_provfld[std_name] = 'where'
            elif fn == 'api_url':
                stdfld_provfld[std_name] = 'url'
            else:
                stdfld_provfld[std_name] = fn
        return stdfld_provfld
        
# .............................................................................
class ITIS:
    """ITIS constants enumeration
    http://www.itis.gov/ITISWebService/services/ITISService/getAcceptedNamesFromTSN?tsn=183671
    @todo: for JSON output use jsonservice instead of ITISService
    """
    DATA_NAMESPACE = '{http://data.itis_service.itis.usgs.gov/xsd}'
    NAMESPACE = '{http://itis_service.itis.usgs.gov}'
    VIEW_URL = 'https://www.itis.gov/servlet/SingleRpt/SingleRpt'
    # ...........
    # Solr Services
    SOLR_URL = 'https://services.itis.gov'
    TAXONOMY_HIERARCHY_QUERY = 'getFullHierarchyFromTSN'
    VERNACULAR_QUERY = 'getCommonNamesFromTSN'    
    NAMES_FROM_TSN_QUERY = 'getAcceptedNamesFromTSN'
    RECORD_FORMAT = 'https://www.itis.gov/solr_documentation.html'
    COUNT_KEY = 'numFound'
    RECORDS_KEY = 'docs'
    # ...........
    # Web Services
    WEBSVC_URL = 'http://www.itis.gov/ITISWebService/services/ITISService'
    JSONSVC_URL = 'https://www.itis.gov/ITISWebService/jsonservice'
    # wildcard matching
    ITISTERMS_FROM_SCINAME_QUERY = 'getITISTermsFromScientificName'
    SEARCH_KEY = 'srchKey'
    # JSON return tags
    TSN_KEY = 'tsn'
    NAME_KEY = 'nameWInd'
    HIERARCHY_KEY = 'hierarchySoFarWRanks'
    HIERARCHY_TAG = 'hierarchyList'
    RANK_TAG = 'rankName'
    TAXON_TAG = 'taxonName'
    KINGDOM_KEY = 'Kingdom'
    PHYLUM_DIVISION_KEY = 'Division'
    CLASS_KEY = 'Class'
    ORDER_KEY = 'Order'
    FAMILY_KEY = 'Family'
    GENUS_KEY = 'Genus'
    SPECIES_KEY = 'Species'
    URL_ESCAPES = [ [" ", "\%20"] ]
    
    @classmethod
    def get_taxon_view(cls, tsn):
        return '{}?search_topic=TSN&search_value={}'.format(ITIS.VIEW_URL, tsn)

    @classmethod
    def get_taxon_data(cls, tsn):
        return '{}?q=tsn:{}'.format(ITIS.SOLR_URL, tsn)

# .............................................................................
# .                           iDigBio constants                               .
# .............................................................................
class Idigbio:
    """iDigBio constants enumeration"""
    NAMESPACE_URL = ''
    NAMESPACE_ABBR = 'gbif'
    VIEW_URL = 'https://www.idigbio.org/portal/records'
    REST_URL = 'https://search.idigbio.org/v2/view/records'
    # LINK_PREFIX = 'https://www.idigbio.org/portal/records/'
    SEARCH_PREFIX = 'https://search.idigbio.org/v2'
    SEARCH_POSTFIX = 'search'
    COUNT_POSTFIX = 'summary/count'
    OCCURRENCE_POSTFIX = 'records'
    PUBLISHERS_POSTFIX = 'publishers'
    RECORDSETS_POSTFIX = 'recordsets'
    SEARCH_LIMIT = 5000
    ID_FIELD = 'uuid'
    OCCURRENCEID_FIELD = 'occurrenceid'
    LINK_FIELD = 'idigbiourl'
    GBIFID_FIELD = 'taxonid'
    BINOMIAL_REGEX = "(^[^ ]*) ([^ ]*)$"
    RECORD_CONTENT_KEY = 'data'
    RECORD_INDEX_KEY = 'indexTerms'
    QUALIFIER = 'idigbio:'
    QKEY = 'rq'
    QFILTERS = {'basisofrecord': 'preservedspecimen'}
    FILTERS = {'limit': 5000,
               'offset': 0,
               'no_attribution': False}
    COUNT_KEY = 'itemCount'
    RECORDS_KEY = 'items'
    RECORD_FORMAT = 'https://github.com/idigbio/idigbio-search-api/wiki'
    
    @classmethod
    def get_occurrence_view(cls, uuid):
        url = None
        if uuid:
            url = '{}/{}'.format(Idigbio.VIEW_URL, uuid)
        return url

    @classmethod
    def get_occurrence_data(cls, uuid):
        url = None
        if uuid:
            url = '{}/{}'.format(Idigbio.REST_URL, uuid)
        return url
    

