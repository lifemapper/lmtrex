from itertools import combinations

from lmtrex.frontend.helpers import provider_label_to_icon_url
from lmtrex.frontend.field_mapper import map_fields
from lmtrex.frontend.reorder_fields import reorder_fields

def flatten_array(array):
    return [item for sublist in array for item in sublist]

# Exclude these fields from the output
fields_to_exclude = [
    'internal:service',
    'internal:provider',
    's2n:view_url',
    's2n:api_url',
    's2n:issues',
    's2n:gbif_occurrence_url',
    'dcterms:type',
    'dwc:taxonRank',
    'dcterms:language',
    'dwc:scientificNameAuthorship',
    's2n:worms_isMarine',
    's2n:worms_isBrackish',
    's2n:worms_isFreshwater',
    's2n:worms_isTerrestrial',
    's2n:worms_isExtinct',
    's2n:kingdom',
    'dwc:kingdom',
    'dwc:phylum',
    'dwc:class',
    'dwc:order',
    'dwc:associatedReferences',
    'dwc:associatedSequences',
    'dcterms:accessRights',
    'dcterms:license',
    'dwc:countryCode',
]

fields_to_exclude_specific = [
    {
        "service": "name",
        "provider": "itis",
        "field": "s2n:hierarchy",
    },
    {
        "service": "name",
        "provider": "worms",
        "field": "s2n:hierarchy",
    }
]

def unique_keys(array):
    seen = set()
    return [x for x in array if not (x in seen or seen.add(x))]

def get_response_keys(responses):
    keys = [set(response.keys()) for response in responses]
    common_keys = set(flatten_array([a & b for a, b in combinations(keys, 2)]))
    all_keys = [
        *flatten_array([
            [
                key
                for key in response.keys()
                if key in common_keys
            ] for response in responses
        ]),
        *flatten_array([
            [
                key
                for key in response.keys()
                if key not in common_keys
            ] for response in responses
        ])
    ]
    return [
        key for key in unique_keys(all_keys) if key not in fields_to_exclude
    ]

def get_value(response, key):
    if key not in response:
        return ''
    for item in fields_to_exclude_specific:
        if item['field'] == key \
            and item['service'] == response['internal:service'] \
            and item['provider'] == response['internal:provider']['code']:
            return ''

    return response[key]


def response_to_table(responses):
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

    dictionary = {}
    for key in get_response_keys(responses):
        dictionary[key] = [
            get_value(response,key)
            for response in responses
        ]

    return header_row, map_fields(reorder_fields(dictionary))