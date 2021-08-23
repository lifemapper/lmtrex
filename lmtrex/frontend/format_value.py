# -*- coding: utf-8 -*-
"""Format different parts of the response object."""

from typing import Dict, List


def format_list(values: List[any]) -> str:
    """
    Format a list.

    Args:
        values: list

    Returns:
        str:
            formatted list
    """
    if not values:
        return "(no data)"
    else:
        fields = {
            "[%d]" % index: value for index, value in enumerate(values)
        }
        return format_dict(fields, is_list_of_values=True)


def format_string(value: str) -> str:
    """
    Format a string.

    Args:
        value: str

    Returns:
        str:
            formatted string
    """
    return f"""<label class="textbox-container">
        <div
            class="textbox"
            aria-role="textbox"
            aria-multiline="true"
            aria-readonly="true"
        >{value}</div>
    </label>"""


def format_value(value: any) -> str:
    """
    Format a value, depending on its type.

    Args:
        value: any

    Returns:
        str:
            formatted value
    """
    if type(value) is bool:
        return f"""<label class="checkbox-with-indicator">
            <input
                type="checkbox"
                onclick="return false;"
                {'checked="checked"' if value else ''}
            >
            <span></span>
        </label>"""
    if type(value) is list:
        return format_list(values=value)
    if type(value) is dict:
        return format_dict(fields=value)
    else:
        return format_string(value=value)


def format_line(
    label: str,
    value: str,
):
    """
    Format a line.

    Args:
        label: Line's label
        value: Line's content (HTML)

    Returns:
        str:
            formatted line
    """
    return f"""<div class="field">
        <div class="label {
            'dictionary-label'
            if value.startswith('<div class="list-of-fields')
            else ''
        }">
            {label}
        </div>
        <div class="value">{value}</div>
    </div>
    """


def format_dict(
    fields: Dict[str, any], is_list_of_values: bool = False
) -> str:
    """
    Format a dict.

    Args:
        fields (Dict[str,any]): dictionary to format
        is_list_of_values (bool):
            whether a dictionary is a list with numeric indexes

    Returns:
        str:
            formatted list
    """
    if not fields:
        return "(no data)"
    else:
        fields = [
            format_line(label, format_value(value))
            for label, value in fields.items()
        ]
        return f"""<div class="list-of-fields {
            'list-of-values' if is_list_of_values else ''
        }">{
            ''.join(fields)
        }</div>"""

