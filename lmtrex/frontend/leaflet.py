from lmtrex.frontend.helpers import provider_label_to_icon_url
from lmtrex.frontend.templates import template
import json


def leaflet(map_info):

    print(json.dumps(map_info))

    if len(map_info['records']) == 0 \
        or len(map_info['errors']) > 0 \
        or len(map_info['records'][0]['errors']) > 0 \
        or map_info['records'][0]['provider']['code'] != 'lm' \
        or len(map_info['records'][0]['records']) == 0:
        return []

    return [{
        'icon_url':
            provider_label_to_icon_url(map_info["provider"]['code']),
        'label': f'{map_info["provider"]["label"]} Projection Map',
        'anchor': map_info["provider"]['code'],
        'content': template('leaflet', {'map_info':json.dumps(map_info)})
    }]