field_order = {
    'gbif:acceptedScientificName': {'after': 'dwc:scientificName'},
    'dwc:datasetName': {'after': 'dwc:specificEpithet'},
}


def from_entries(entries):
    return {key:value for key,value in entries}

def reorder_fields(mapped_table):
    for field_name, position in field_order.items():
        if field_name not in mapped_table:
            continue

        if 'after' not in position:
            continue

        if position['after'] not in mapped_table:
            continue

        table = list(mapped_table.items())
        keys = list(mapped_table.keys())
        current_position = keys.index(field_name)
        target_position = keys.index(position['after'])
        current_entry = table.pop(current_position)
        if current_position > target_position:
            target_position += 1

        table.insert(target_position, current_entry)
        mapped_table = from_entries(table)

    return mapped_table