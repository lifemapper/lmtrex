import json

from lmtrex.frontend.helpers import provider_label_to_icon_url
from lmtrex.frontend.templates import template
from lmtrex.services.api.v1.map import MapSvc


def leaflet(occurrence_info, name_info, scientific_name):
    map_info = MapSvc().GET(namestr=scientific_name)
    return {
        'icon_url':
            provider_label_to_icon_url(map_info["provider"]['code']),
        'label': f'{map_info["provider"]["label"]} Projection Map',
        'anchor': map_info["provider"]['code'],
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