import os

root_dir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    # Database settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(root_dir, 'tags_data.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Services settings
    AUTH_SERVICE_URL = 'https://places-info-auth.herokuapp.com'

    # Other settings
    GUI_APP = 'gui'
    GATEWAY_APP = 'gateway'
    REQUEST_APP = 'tags'
    JSON_AS_ASCII = False
    JSONIFY_PRETTYPRINT_REGULAR = True
    SECRET_KEY = 'places-info-tags-secret-key'
