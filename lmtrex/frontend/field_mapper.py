"""Convert field names to field labels."""

import re

from lmtrex.frontend.format_value import format_value

# Replace a word with a mapped variant
from lmtrex.frontend.templates import template

field_part_mapper = {
    'gbif': 'GBIF',
    'idigbio': 'iDigBio',
    'itis': 'ITIS',
    'id': 'ID',
    'uuid': 'UUID',
    'url': 'URL',
    'tsn': 'TSN',
    'lsid': 'LSID',
    'worms': 'WoRMS',
}

# Replace field name with a label
label_mapper = {
    'idigbio:uuid': 'iDigBio Record UUID',
    'mopho:specimen.specimen_id': 'MorphoSource ID',
    'dwc:stateProvince': 'State/Province',
    'gbif:gbifID': 'GBIF Record ID',
    'gbif:publishingOrgKey': 'GBIF Publisher ID',
    's2n:specify_identifier': 'Specify Record ID',
    'dcterms:modified': 'Modified by Host',
    'dwc:decimalLongitude': 'Longitude',
    'dwc:decimalLatitude': 'Latitude',
    's2n:worms_match_type': 'WoRMS Match Type'
}

def extract_morphosource_id(link):
    if not link or not link.startswith('https://www'):
        return False
    match = re.search(r'/[^/]+$', link)
    return match.group()[1:] if match else False

# Replace field value with a transformed value
value_mapper = {
    'gbif:publishingOrgKey': lambda publishing_org_key:
        template(
            'link',
            dict(
                href=f'https://www.gbif.org/publisher/{publishing_org_key}',
                label=publishing_org_key
            )
        ) if publishing_org_key else '',
    'mopho:specimen.specimen_id': lambda specimen_view_url:
        template(
            'link',
            dict(
                href=specimen_view_url,
                label=extract_morphosource_id(specimen_view_url)
            )
        ) if extract_morphosource_id(specimen_view_url)
        else specimen_view_url if specimen_view_url else ''
}

merge_fields = [
    {
        'field_names': ['dwc:year', 'dwc:month', 'dwc:day'],
        'label': 'Collection Date',
        'title': 'dwc:month / dwc:day / dwc:year',
        'merge_function': lambda year, month, day:
            '' if None in [year, month, day]
            else template(
                'date',
                dict(
                    value=f'{year}-{month.zfill(2)}-{day.zfill(2)}',
                    label='Collection Date'
                )
            )
    }
]


def label_from_field_name(field_name: str) -> str:

    striped_field_name = re.sub(r'^\w+:','',field_name)
    formatted_field_name = re.sub(
        r'([a-z])([A-Z])',
        r'\1 \2',
        striped_field_name
    )
    converted_field_name = ' '.join([
        field_part.capitalize()
        for field_part in formatted_field_name.split('_')
    ])

    mapped_field_name = [
        field_part_mapper[field_part.lower()]
            if field_part.lower() in field_part_mapper
            else field_part
        for field_part in converted_field_name.split(' ')
    ]
    if mapped_field_name[0].lower() in label_mapper:
        mapped_field_name[0] = label_mapper[mapped_field_name[0]]
    joined_field_name = ' '.join(mapped_field_name)

    capitalized_field_name = \
        joined_field_name[0].upper() + joined_field_name[1:]

    return capitalized_field_name


regex_link = r"^((([A-Za-z]{3,9}:(?:\/\/)?)(?:[-;:&=\+\$,\w]+@)?[A-Za-z0-9.-]+|(?:www.|[-;:&=\+\$,\w]+@)[A-Za-z0-9.-]+)((?:\/[\+~%\/.\w\-_]*)?\??(?:[-\+=&;%@.\w_]*)#?(?:[\w]*))?)$"
def is_link(value):
    return re.search(regex_link, value)


def default_value_formatter(value):
    if value is None:
        return ''
    elif type(value) == str and is_link(value):
        return template(
            'link',
            dict(
                href=value,
                label=value
            )
        )
    elif type(value) in [str, int, float]:
        return value
    else:
        return format_value(value)

def transpose(target_list):
    return list(zip(*target_list))

def map_fields(dictionary):
    mapped_table = []
    merged_fields = []
    for field_name, values in dictionary.items():

        if field_name in merged_fields:
            continue

        label = \
            label_mapper[field_name] \
            if field_name in label_mapper \
            else label_from_field_name(field_name)

        resolved_value_mapper = None
        mapped_values = None

        if field_name in value_mapper:
            resolved_value_mapper = value_mapper[field_name]
        else:
            for mapping in merge_fields:
                if field_name in mapping['field_names']:
                    label = mapping['label']
                    field_values = transpose([
                        dictionary[field_name]
                        if field_name in dictionary
                        else None
                        for field_name in mapping['field_names']
                    ])
                    mapped_values = [
                        mapping['merge_function'](*values)
                        for values in field_values
                    ]
                    field_name = mapping['title']
                    merged_fields.extend(mapping['field_names'])
                    break

        if resolved_value_mapper is None:
            resolved_value_mapper = default_value_formatter

        if not mapped_values:
            mapped_values = [
                resolved_value_mapper(value) for value in values
            ]

        mapped_table.append([
            field_name,
            label,
            *mapped_values
        ])

    return mapped_table