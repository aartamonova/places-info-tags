from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

api = Api(app)

from tags.tags_resource import TagListResource, TagAddResource, TagResource, TagListResource, PlaceTagAddResource, \
    PlaceTagEditResource, TagPlaceListResource, PlaceTagListResource

api.add_resource(TagResource, '/tags/<int:tag_id>')
api.add_resource(TagListResource, '/tags')
api.add_resource(TagAddResource, '/tags')
api.add_resource(TagPlaceListResource, '/places/<int:place_id>/tags')
api.add_resource(PlaceTagListResource, '/tags/<int:tag_id>/places')
api.add_resource(PlaceTagAddResource, '/places/tags/add')
api.add_resource(PlaceTagEditResource, '/places/tags/edit')

# Migration
from tags import tags_model
