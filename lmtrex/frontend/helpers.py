def provider_label_to_icon_url(provider_label):
    return (
        f'/api/v1/badge/?provider={provider_label}&icon_status=active'
    )