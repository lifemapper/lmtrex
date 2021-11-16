from flask import Flask, Blueprint, request
from markupsafe import escape

from lmtrex.flask_app.broker.occ import OccurrenceSvc

# bp = Blueprint('occ', __name__, url_prefix='/occ')
app = Flask(__name__)


@app.route("/")
def index():
    return "<p>Hello, World!</p>"

# .....................................................................................
@app.route("/hello")
def hello():
    return "<p>Hello, Brave New World!</p>"

# .....................................................................................
@app.route("/name/<name>")
def name(name):
    return f"Hello, {escape(name)}!"

# .....................................................................................
@app.route("/api/v1/occ")
def occ_endpoint():
    response = OccurrenceSvc.get_endpoint()
    return response

# .....................................................................................
@app.route('/api/v1/occ/<string:identifier>', methods=['GET'])
def occ_get(identifier):
    """Get an occurrence record from available providers.

    Args:
        identifier (str): An occurrence identifier to search for among occurrence providers.

    Returns:
        dict: A dictionary of metadata for the requested record.
    """
    # response = OccurrenceSvc.get_occurrence_records(occid='identifier')
    provider = request.args.get('provider', default = None, type = str)
    dataset_key = request.args.get('dataset_key', default = None, type = str)
    count_only = request.args.get('count_only', default = 'False', type = str)
    response = OccurrenceSvc.get_occurrence_records(
        occid=identifier, provider=provider, dataset_key=dataset_key, count_only=count_only)
    return response



"""
To run in debug mode, from directory containing flask app
export FLASK_ENV=development
export FLASK_APP=routes
flask run
"""