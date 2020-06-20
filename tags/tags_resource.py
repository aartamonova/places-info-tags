import functools
import json
import logging

import requests
from flask import request, make_response, jsonify
from flask_api.status import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_200_OK, HTTP_400_BAD_REQUEST, \
    HTTP_403_FORBIDDEN
from flask_restful import fields, marshal, Resource

from config import Config
from tags.tags_model import TagData, PlaceTagData

tag_fields = {'id': fields.Integer,
              'name': fields.String,
              'added_by': fields.String}

tag_list_fields = {'count': fields.Integer,
                   'tags': fields.List(fields.Nested(tag_fields))}

place_fields = {'id': fields.Integer}

place_list_fields = {'count': fields.Integer,
                     'places': fields.List(fields.Nested(place_fields))}

logging.basicConfig(filename="log_data.log", level=logging.WARNING, filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')


def access_token_required(foo):
    @functools.wraps(foo)
    def wrapper(*args, **kwargs):
        if 'Gui-Token' or 'Gateway-Token' in request.headers:
            if 'Gui-Token' in request.headers:
                source_app = Config.GUI_APP
                access_token = request.headers['Gui-Token']
            else:
                source_app = Config.GATEWAY_APP
                access_token = request.headers['Gateway-Token']

            # Проверить токен
            try:
                response = requests.get(Config.AUTH_SERVICE_URL + '/token/validate', 'source_app=' +
                                        str(source_app) + '&request_app=' + str(Config.REQUEST_APP) +
                                        '&access_token=' + str(access_token))
            except:
                return make_response(jsonify({'error': 'Invalid authorization data'}), HTTP_403_FORBIDDEN)

            if response.status_code != HTTP_200_OK:
                return make_response(jsonify({'error': 'Invalid authorization data'}), HTTP_403_FORBIDDEN)

            return foo(*args, **kwargs)
        else:
            return make_response(jsonify({'error': 'Invalid authorization data'}), HTTP_403_FORBIDDEN)

    return wrapper


class TagResource(Resource):
    @staticmethod
    @access_token_required
    def get(tag_id):
        tag = TagData.get_by_id(tag_id)
        logging.warning('Поиск тега с id %s' % tag_id)
        if not tag:
            return make_response(jsonify({'error': 'The tag with the selected name does not exist'}),
                                 HTTP_404_NOT_FOUND)
        else:
            try:
                content = make_response(marshal(tag, tag_fields), HTTP_200_OK)
            except:
                return make_response(jsonify({'error': 'Corrupted database data'}), HTTP_500_INTERNAL_SERVER_ERROR)

            return make_response(content, HTTP_200_OK)

    @staticmethod
    @access_token_required
    def delete(tag_id):
        tag = TagData.get_by_id(tag_id)
        logging.warning('Удаление тега с id %s' % tag_id)
        if not tag:
            return make_response(jsonify({'error': 'The tag with the selected id does not exist'}),
                                 HTTP_404_NOT_FOUND)
        else:
            TagData.delete(tag_id)
            return make_response(jsonify({'message': 'Tag was deleted successfully'}), HTTP_200_OK)


class TagAddResource(Resource):
    @staticmethod
    @access_token_required
    def post():
        try:
            name = json.loads(request.data.decode("utf-8"))['name']
            added_by = json.loads(request.data.decode("utf-8"))['added_by']
        except:
            return make_response(jsonify({'error': 'Invalid tag data'}), HTTP_400_BAD_REQUEST)

        tag = TagData.create(name, added_by)
        logging.warning('Создание тега с названием %s' % name)
        if not tag:
            return make_response(jsonify({'error': 'The tag not created'}), HTTP_404_NOT_FOUND)
        else:
            try:
                make_response(marshal(tag, tag_fields), HTTP_200_OK)
            except:
                return make_response(jsonify({'error': 'Corrupted database data'}), HTTP_500_INTERNAL_SERVER_ERROR)
            return make_response(marshal(tag, tag_fields), HTTP_200_OK)


class TagListResource(Resource):
    @staticmethod
    @access_token_required
    def get():
        tags = TagData.get_all()
        logging.warning('Получение всех тегов')
        if not tags:
            return make_response(jsonify({'error': 'The tag database is empty'}), HTTP_404_NOT_FOUND)
        else:
            try:
                content = marshal({'count': len(tags), 'tags': [marshal(t, tag_fields) for t in tags]},
                                  tag_list_fields)
            except:
                return make_response({'error': 'Corrupted database data'}, HTTP_500_INTERNAL_SERVER_ERROR)

            return make_response(content, HTTP_200_OK)


class TagPlaceListResource(Resource):
    @staticmethod
    @access_token_required
    def get(place_id):
        '''Получить список тегов по id места'''
        tags = PlaceTagData.get_all_by_place_id(place_id)
        logging.warning('Получение всех тегов для места с id %s' % place_id)
        if not tags:
            return make_response(jsonify({'error': 'The database is empty'}), HTTP_404_NOT_FOUND)
        else:
            try:
                content = marshal({'count': len(tags), 'tags': [marshal(t, tag_fields) for t in tags]},
                                  tag_list_fields)
            except:
                return make_response({'error': 'Corrupted database data'}, HTTP_500_INTERNAL_SERVER_ERROR)

            return make_response(content, HTTP_200_OK)


class PlaceTagListResource(Resource):
    @staticmethod
    @access_token_required
    def get(tag_id):
        '''Получить список id мест по id тега'''
        places = PlaceTagData.get_all_by_tag_id(tag_id)
        logging.warning('Получить список мест для тега с id %s' % tag_id)
        if not places:
            return make_response(jsonify({'error': 'The database is empty'}), HTTP_404_NOT_FOUND)
        else:
            try:
                content = marshal({'count': len(places), 'places': [marshal(p, place_fields) for p in places]},
                                  place_list_fields)
            except:
                return make_response({'error': 'Corrupted database data'}, HTTP_500_INTERNAL_SERVER_ERROR)

            return make_response(content, HTTP_200_OK)


class PlaceTagAddResource(Resource):
    @staticmethod
    @access_token_required
    def post():
        try:
            place_id = json.loads(request.data.decode("utf-8"))['place_id']
            tags = json.loads(request.data.decode("utf-8"))['tags']
        except:
            return make_response(jsonify({'error': 'Invalid tag data'}), HTTP_400_BAD_REQUEST)

        result = PlaceTagData.create(place_id, tags)
        logging.warning('Создание ассоциации тегов с местом с id %s' % place_id)
        if not result:
            return make_response(jsonify({'error': 'The tag not created'}), HTTP_404_NOT_FOUND)
        else:
            return make_response({'info': 'Success added tags'}, HTTP_200_OK)


class PlaceTagEditResource(Resource):
    @staticmethod
    @access_token_required
    def post():
        try:
            place_id = json.loads(request.data.decode("utf-8"))['place_id']
            tags = json.loads(request.data.decode("utf-8"))['tags']
        except:
            return make_response(jsonify({'error': 'Invalid tag data'}), HTTP_400_BAD_REQUEST)

        result = PlaceTagData.edit(place_id, tags)
        logging.warning('Изменение ассоциации тегов с местом с id %s' % place_id)
        if not result:
            return make_response(jsonify({'error': 'The tag not created'}), HTTP_404_NOT_FOUND)
        else:
            return make_response({'info': 'Success added tags'}, HTTP_200_OK)
