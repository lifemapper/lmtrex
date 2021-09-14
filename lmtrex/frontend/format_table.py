from typing import List, Dict

from lmtrex.frontend.templates import template


def table_data_to_html(
    header_row: List[Dict[str, str]],
    rows: List[List[str]],
) -> str:
    return template(
        'table',
        dict(
            class_name='data',
            header=template(
                'thead',
                dict(
                    header=[
                        template('td', dict(cell='')),
                        *[
                            template(
                                'th_for_col',
                                {
                                    'icon_url': header_cell['icon_url'],
                                    'label': f"""{header_cell['label']} {
                                        template(
                                            'link',
                                            dict(
                                                href=header_cell['view_url'],
                                                label='(link)'
                                            )
                                        )
                                    }"""
                                } if header_cell['view_url'] else header_cell
                            )
                            for header_cell in header_row
                        ]
                    ]
                )
            ),
            body=[
                template(
                    'tr',
                    dict(
                        class_name='identical' \
                            if len(set([cell for cell in cells if cell]))==1
                            else '',
                        cells=[
                            template(
                                'th_for_row',
                                dict(
                                    field_name=field_name,
                                    label=label,
                                )
                            ),
                            *[
                                template(
                                    'td',
                                    dict(
                                        cell=cell
                                    )
                                )
                                for cell in cells
                            ]
                        ]
                    )
                ) for field_name, label, *cells in rows
            ]
        )
    ) if rows else ''
