provider_icon_mapper = {
    'Lifemapper': 'lm',
    'MorphoSource': 'mopho',
    'GBIF': 'gbif',
    'iDigBio': 'idb',
    'ITIS': '',
    'Specify': '',
}

def provider_label_to_icon_url(provider_label):
    return (
        f'https://broker-dev.spcoco.org/api/v1/badge/?provider='
        f'{provider_icon_mapper[provider_label]}'
        f'&icon_status=active')