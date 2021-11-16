from flask import Flask, Blueprint, request
from markupsafe import escape

from lmtrex.flask_app.broker.address import AddressSvc
from lmtrex.flask_app.broker.badge import BadgeSvc
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
@app.route("/api/v1/address")
def address_endpoint():
    response = AddressSvc.get_endpoint()
    return response

# .....................................................................................
@app.route("/api/v1/badge")
def badge_endpoint():
    response = BadgeSvc.get_endpoint()
    return response

# .....................................................................................
@app.route('/api/v1/badge/<string:provider>', methods=['GET'])
def badge_get(provider):
    """Get an occurrence record from available providers.

    Args:
        provider (str): An provider code for which to return an icon.

    Returns:
        dict: An image file as binary or an attachment.
    """
    # response = OccurrenceSvc.get_occurrence_records(occid='identifier')
    # provider = request.args.get('provider', default = None, type = str)
    icon_status = request.args.get('icon_status', default = 'active', type = str)
    stream = request.args.get('stream', default = 'True', type = str)
    response = BadgeSvc.get_icon(
        provider=provider, icon_status=icon_status, stream=stream, app_path=app.root_path)
    return response


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