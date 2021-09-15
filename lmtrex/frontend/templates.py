import os
from string import Template

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
    signature = f'/*{file_path}*/\n\n' \
        if file_path.endswith('css') or file_path.endswith('js') \
        else ''
    with open(os.path.join(base_dir,file_path), 'r', encoding='utf-8') as file:
        return f'{signature}{file.read()}'

frontend_static_files = None

def frontend_template():
    global frontend_static_files
    if not frontend_static_files or is_development:
        frontend_static_files = {
            key: inline_static(file_path)
            for key, file_path in [
                ['main_styles', 'static/css/main.css'],
                ['frontend_styles', 'static/css/frontend.css'],
                ['loader_styles', 'static/css/loader.css'],
                ['response_styles', 'static/css/response.css'],
                ['leaflet_styles', 'static/css/leaflet.css'],
                ['table_styles', 'static/css/table.css'],
                [
                    'specify_network_square',
                    'static/img/specify_network_square.svg'
                ],
                ['utils_script', 'static/js/utils.js'],
                ['leaflet_extend_script', 'static/js/leafletExtend.js'],
                ['config_script', 'static/js/config.js'],
                ['leaflet_script', 'static/js/leaflet.js'],
                ['loader_script', 'static/js/loader.js'],
                ['response_collapse_script', 'static/js/responseCollapse.js'],
                ['frontend_script', 'static/js/frontend.js'],
            ]
        }
    return template('frontend', frontend_static_files)

stats_static_files = None

def stats_template(body):
    global stats_static_files
    if not stats_static_files or is_development:
        stats_static_files = {
            key: inline_static(file_path)
            for key, file_path in [
                ['main_styles', 'static/css/main.css'],
                ['stats_styles', 'static/css/stats.css'],
                ['loader_styles', 'static/css/loader.css'],
                ['leaflet_styles', 'static/css/leaflet.css'],
                ['slider_styles', 'static/css/slider.css'],
                [
                    'specify_network_square',
                    'static/img/specify_network_square.svg'
                ],
                ['utils_script', 'static/js/utils.js'],
                ['leaflet_extend_script', 'static/js/leafletExtend.js'],
                ['config_script', 'static/js/config.js'],
                ['collection_stats_script', 'static/js/collectionStats.js'],
                ['loader_script', 'static/js/loader.js'],
                ['stats_script', 'static/js/stats.js'],
            ]
        }
    return template('stats', {
        **stats_static_files,
        'body': body,
    })
