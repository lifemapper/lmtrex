from itertools import combinations

from lmtrex.frontend.helpers import provider_label_to_icon_url
from lmtrex.frontend.field_mapper import map_fields

def flatten_array(array):
    return [item for sublist in array for item in sublist]

# Exclude these fields from the output
fields_to_exclude = [
    'internal:service',
    'internal:provider',
    's2n:view_url',
    's2n:api_url',
    's2n:issues',
    's2n:hierarchy'
    's2n:gbif_occurrence_url'
]

def get_response_keys(responses):
    keys = [set(response.keys()) for response in responses]
    common_keys = set(flatten_array([a & b for a, b in combinations(keys, 2)]))
    all_keys = [
        *common_keys,
        *flatten_array([
            [
                key
                for key in response.keys()
                if key not in common_keys
            ] for response in responses
        ])
    ]
    return [key for key in all_keys if key not in fields_to_exclude]

def response_to_table(responses):

    # FIXME: remove this
    responses = [
        *[response for response in responses if response['internal:provider']['code']=='specify'],
        *[response for response in responses if
          response['internal:provider']['code'] != 'specify'],
    ]

    header_row = []
    for response in responses:
        label = response['internal:provider']['label']
        view_url = \
            response['s2n:view_url'] \
            if 's2n:view_url' in response \
            else None
        icon_url = \
            provider_label_to_icon_url(response["internal:provider"]['code'])
        header_row.append(dict(
            label=label,
            view_url=view_url,
            icon_url=icon_url
        ))

    rows = []
    for key in get_response_keys(responses):
        rows.append([
            key,
            *[
                response[key]
                if key in response
                else ''
                for response in responses
            ]
        ])

    return header_row, map_fields(rows)