"""Convert field names to field labels."""

import re

from lmtrex.frontend.format_value import format_list, format_value

# Replace a word with a mapped variant
from lmtrex.frontend.templates import template

field_part_mapper = {
    'gbif': 'GBIF',
    'idigbio': 'iDigBio',
    'itis': 'ITIS',
    'id': 'ID',
    'uuid': 'UUID',
    'url': 'URL',
}

# Replace field name with a label
label_mapper = {
    'idigbio:uuid': 'iDigBio UUID',
    'mopho:specimen.specimen_id': 'MorphoSource Specimen ID',
}

# Replace field name and field value with label and a transformed value
value_mapper = {

}


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

def map_fields(table):
    mapped_table = []
    for row in table:
        field_name, *values = row

        label = \
            label_mapper[field_name] \
            if field_name in label_mapper \
            else label_from_field_name(field_name)

        resolved_value_mapper = \
            value_mapper[field_name] \
            if field_name in value_mapper \
            else default_value_formatter

        mapped_values = [
            resolved_value_mapper(value) for value in values
        ]

        mapped_table.append([
            field_name,
            label,
            *mapped_values
        ])

    return mapped_table