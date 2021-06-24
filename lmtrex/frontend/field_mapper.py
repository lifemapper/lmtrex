"""Convert field names to field labels."""

import re

# Replace a word with a mapped variant
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
    'idigbio:uuid': 'iDigBio UUID'
}

# Replace field name and field value with label and a transformed value
field_mapper = {
    # 's2n:idigbio_flags': lambda value:
    #     ('iDigBio Flags', value)
}

# Exclude these fields from the output
fields_to_exclude = [
    's2n:service',
    's2n:provider',
    's2n:view_url',
    's2n:api_url',
]

def default_field_mapper(field_name, value):

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

    return capitalized_field_name, value


def map_fields(response):
    result = {}
    for field_name, value in response.items():
        if field_name in fields_to_exclude:
            continue

        elif field_name in label_mapper:
            final_field_name, final_field_value = \
                label_mapper[field_name], value

        elif field_name in field_mapper:
            final_field_name, final_field_value = \
                field_mapper[field_name](value)

        else:
            final_field_name, final_field_value = \
                default_field_mapper(field_name, value)

        result[final_field_name] = final_field_value

    return result