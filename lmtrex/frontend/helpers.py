def provider_label_to_icon_url(provider_label):
    return (
        f'https://broker-dev.spcoco.org/api/v1/badge/?provider='
        f'{provider_label}&icon_status=active'
    )