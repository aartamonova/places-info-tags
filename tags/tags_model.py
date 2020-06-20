from tags import db


class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    added_by = db.Column(db.String(20))


class PlaceTag(db.Model):
    __tablename__ = 'places_tags'

    id = db.Column(db.Integer, primary_key=True)
    place_id = db.Column(db.Integer)
    tag_id = db.Column(db.Integer)


class TagData:
    @staticmethod
    def get_by_id(tag_id):
        tag = Tag.query.filter_by(id=tag_id).first()
        return tag

    @staticmethod
    def get_by_name(name):
        tag = Tag.query.filter_by(name=name).first()
        return tag

    @staticmethod
    def get_all():
        tags = Tag.query.all()
        return tags

    @staticmethod
    def create(name, added_by):
        old_tag = TagData.get_by_name(name)
        if not old_tag:
            tag = Tag(name=name, added_by=added_by)
            if tag:
                db.session.add(tag)
                db.session.commit()
                return tag
        return None

    @staticmethod
    def delete(tag_id):
        tag = TagData.get_by_id(tag_id)
        if tag:
            place_tags = PlaceTagData.get_by_tag_id(tag_id)
            for place_tag in place_tags:
                PlaceTagData.delete(place_tag.id)

            db.session.delete(tag)
            db.session.commit()


class Place:
    def __init__(self, place_id):
        self.id = place_id


class PlaceTagData:
    @staticmethod
    def get_by_id(place_tag_id):
        place_tag = PlaceTag.query.filter_by(id=place_tag_id).first()
        return place_tag

    @staticmethod
    def get_by_ids(tag_id, place_id):
        place_tag = PlaceTag.query.filter_by(tag_id=tag_id, place_id=place_id).first()
        return place_tag

    @staticmethod
    def get_by_place_id(place_id):
        place_tags = PlaceTag.query.filter_by(place_id=place_id).all()
        return place_tags

    @staticmethod
    def get_by_tag_id(tag_id):
        place_tags = PlaceTag.query.filter_by(tag_id=tag_id).all()
        return place_tags

    @staticmethod
    def get_all_by_place_id(place_id):
        '''Получить все теги для указанного места'''
        db.session.commit()
        place_tags = PlaceTagData.get_by_place_id(place_id)
        if place_tags:
            tags = []
            for place_tag in place_tags:
                tags.append(TagData.get_by_id(place_tag.tag_id))
            return tags
        return None

    @staticmethod
    def get_all_by_tag_id(tag_id):
        '''Получить все id мест для указанного тега'''
        db.session.commit()
        place_tags = PlaceTagData.get_by_tag_id(tag_id)
        if place_tags:
            places = []
            for place_tag in place_tags:
                places.append(Place(place_tag.place_id))
            return places
        return None

    @staticmethod
    def edit(place_id, tags):
        place_tags = PlaceTagData.get_by_place_id(place_id)
        for place_tag in place_tags:
            PlaceTagData.delete(place_tag.id)
        return PlaceTagData.create(place_id, tags)

    @staticmethod
    def create(place_id, tags):
        place_id = int(place_id)
        for tag in tags:
            tag_id = int(tag)
            old_place_tag = PlaceTagData.get_by_ids(tag_id, place_id)
            if not old_place_tag:
                place_tag = PlaceTag(tag_id=tag_id, place_id=place_id)
                if place_tag:
                    db.session.add(place_tag)
                    db.session.commit()
        place_tags = PlaceTagData.get_all_by_place_id(place_id)
        if place_tags:
            return True
        return False

    @staticmethod
    def delete(place_tag_id):
        place_tag = PlaceTagData.get_by_id(place_tag_id)
        if place_tag:
            db.session.delete(place_tag)
            db.session.commit()
