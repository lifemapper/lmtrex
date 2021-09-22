import os
from string import Template
import random
import json

base_dir = os.path.dirname(os.path.realpath(__file__))
templates_dir = os.path.join(base_dir, 'templates/')

templates = dict()

is_development = True

def template(name, arguments):
    if name not in templates or is_development:
        with open(os.path.join(templates_dir, f'{name}.html')) as file:
            templates[name] = Template(file.read()).substitute
    return templates[name](
        {
            key:''.join(value) if type(value) == list else value
            for key, value in arguments.items()
        }
    )


def inline_static(file_path):
    signature = f'/* {file_path} */\n\n' \
        if file_path.endswith('css') or file_path.endswith('js') \
        else ''
    with open(os.path.join(base_dir,file_path), 'r', encoding='utf-8') as file:
        return f'{signature}{file.read()}'

frontend_static_files = None

def get_loading_tagline():
    return f"""{random.choice([
        'Searching',
        'Running',
        'Exploring',
        'Hustling',
        'Gathering',
        'Hacking',
        'Pursuing',
        'Going after',
        'Assembling',
        'Fetching',
        'Grabbing',
        'Loading'
    ])}..."""

def get_bundle_location(name):
    manifest = json.loads(inline_static('js_src/dist/manifest.json'))
    file_name = os.path.basename(manifest[name])
    return f'js_src/dist/{file_name}'

def frontend_template():
    global frontend_static_files
    if not frontend_static_files or is_development:
        frontend_static_files = {
            key: inline_static(file_path)
            for key, file_path in [
                [
                    'specify_network_square',
                    'js_src/static/img/specify_network_square.svg'
                ],
                [
                    'bundle',
                    get_bundle_location('frontend.js')
                ]
            ]
        }
    return template('index', {
        **frontend_static_files,
        'tagline': get_loading_tagline(),
        'description': (
            'This page compares the information contained in a specimen record '
            'in a Specify database with that held by biodiversity aggregators '
            'and name authorities. The page includes responses from global '
            'providers on the occurrence, taxonomy and geographic distribution '
            'of the species.'
        ),
        'body': '',
    })

stats_static_files = None

def stats_template(body):
    global stats_static_files
    if not stats_static_files or is_development:
        stats_static_files = {
            key: inline_static(file_path)
            for key, file_path in [
                [
                    'specify_network_square',
                    'js_src/static/img/specify_network_square.svg'
                ],
                [
                    'bundle',
                    get_bundle_location('stats.js')
                ]
            ]
        }
    return template('index', {
        **stats_static_files,
        'tagline': get_loading_tagline(),
        'description': (
            'The maps on this page visualize the geographic locality of the '
            'digitized biological specimens held in museums and herbaria as '
            'reported to GBIF. The first map shows all vouchered species '
            'occurrence points by biological discipline within an institution. '
            'The second map visualizes the point localities for all digitized '
            'specimens, for all species, across all disciplines within an '
            'institution.'
        ),
        'body': body,
    })
