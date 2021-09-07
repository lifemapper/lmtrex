import os
from string import Template

base_dir = os.path.dirname(os.path.realpath(__file__))
templates_dir = os.path.join(base_dir, 'templates/')

templates = dict()


def template(name, arguments):
    if name not in templates:
        with open(os.path.join(templates_dir, f'{name}.html')) as file:
            templates[name] = Template(file.read()).substitute
    return templates[name](
        {
            key:''.join(value) if type(value) == list else value
            for key, value in arguments.items()
        }
    )


def inline_static(file_path):
    with open(os.path.join(base_dir,file_path), 'r', encoding='utf-8') as file:
        return file.read()



static_files = None

def index_template(body):
    global static_files
    if not static_files:
        static_files = {
            key: inline_static(file_path)
            for key, file_path in [
                ['main_styles', 'static/css/styles.css'],
                ['loader_styles', 'static/css/loader.css'],
                ['response_styles', 'static/css/response.css'],
                ['leaflet_styles', 'static/css/leaflet.css'],
                ['table_styles', 'static/css/table.css'],
                ['slider_styles', 'static/css/slider.css'],
                ['main_script', 'static/js/main.js'],
                ['leaflet_extend_script', 'static/js/leafletExtend.js'],
                ['config_script', 'static/js/config.js'],
                ['collection_stats_script', 'static/js/collectionStats.js'],
                ['leaflet_script', 'static/js/leaflet.js'],
            ]
        }
    return template('index', {
        **static_files,
        'body': body,
    })
