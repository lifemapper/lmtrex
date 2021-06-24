import os
from string import Template

base_dir = os.path.dirname(os.path.realpath(__file__))
templates_dir = os.path.join(base_dir, 'templates/')

templates = dict()


def template(name, arguments):
    if name not in templates or True:  # FIXME: remove this part
        with open(os.path.join(templates_dir, f'{name}.html')) as file:
            templates[name] = Template(file.read()).substitute
    return templates[name](arguments)


def inline_static(file_path):
    with open(os.path.join(base_dir,file_path)) as file:
        return file.read()

index_template_store = None

def index_template(body):
    global index_template_store
    if not index_template_store or True:  # FIXME: remove this part
        index_template_store = Template(template('index', {
            **{
                key: inline_static(file_path)
                for key, file_path in [
                    ['main_styles', 'static/css/styles.css'],
                    ['response_styles', 'static/css/response.css'],
                    ['main_script', 'static/js/main.js']
                ]
            },
            'body': '${body}'
        })).substitute
    return index_template_store({'body':body})
