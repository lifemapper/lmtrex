# -*- coding: utf-8 -*-
"""Convert a JSON response to a more human-readable form.

json_to_html accepts a JSON string or a serializable Dict.

It would return an HTML string with a more human-friendly representation of the
json object.

To properly render the resulting string, please also link the
lmtrex/frontend/static/css/styles.css and lmtrex/frontend/static/scripts/main.js
on the resulting page .
"""

import json
from lmtrex.frontend.format_response import format_response


def json_to_html(json_object):
    """Generate an HTML page from a JSON response.

    Args:
        json_object:
            JSON Response object
            (either a JSON string or a serializable Dict)

    Returns:
        HTML for a page
    """
    if type(json_object) is str:
        json_object = json.loads(json_object)

    return format_response(json_object)
