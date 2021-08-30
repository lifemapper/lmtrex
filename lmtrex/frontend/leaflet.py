import json

from lmtrex.frontend.templates import template
from lmtrex.frontend.format_value import serialize_response
from lmtrex.services.api.v1.map import MapSvc


def leaflet(occurrence_info, name_info, scientific_name):
    map_info = serialize_response(MapSvc().GET(namestr=scientific_name))
    return {
        'label': 'Geographic Data',
        'anchor': 'map',
        'content': template(
            'leaflet',
            {
                'map_info': json.dumps(
                    {
                        'occurrence_info': occurrence_info,
                        'name_info': name_info,
                        **map_info,
                    }
                )
            }
        )
    }