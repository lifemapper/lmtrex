import os


BASE_DIR = os.path.dirname(os.path.realpath(__file__))

TEMPLATES_DIR = os.path.join(BASE_DIR, '../collection_stats/static/templates')

COLLECTION_STATS_BASE_DIR = os.path.join(BASE_DIR, '../collection_stats')

COLLECTION_STATS_RELATIVE_LOCATION = 'data'

COLLECTION_STATS_LOCATION = os.path.join(
    BASE_DIR,
    '../collection_stats/%s' % COLLECTION_STATS_RELATIVE_LOCATION
)
