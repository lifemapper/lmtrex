import os
from string import Template

base_dir = os.path.dirname(os.path.realpath(__file__))
templates_dir = os.path.join(base_dir, 'templates/')

templates = dict()


def template(name, arguments):
    if name not in templates:
        with open(os.path.join(templates_dir, f'{name}.html')) as file:
            templates[name] = Template(file.read()).substitute
    return templates[name](arguments)


def inline_static(file_path):
    with open(os.path.join(base_dir,file_path)) as file:
        return file.read()



static_files = None

def index_template(body):
    global static_files
    if not static_files:
        static_files = {
            key: inline_static(file_path)
            for key, file_path in [
                ['main_styles', 'static/css/styles.css'],
                ['response_styles', 'static/css/response.css'],
                ['leaflet_styles', 'static/css/leaflet.css'],
                ['main_script', 'static/js/main.js'],
                ['leaflet_script', 'static/js/leaflet.js']
            ]
        }
    return template('index', {
        **static_files,
        'body': body,
    })
