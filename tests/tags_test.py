import unittest

from alchemy_mock.mocking import UnifiedAlchemyMagicMock, AlchemyMagicMock

from tags.tags_model import Tag


class TestTags(unittest.TestCase):
    def test_get_none(self):
        session = UnifiedAlchemyMagicMock()
        result = session.query(Tag).all()
        return self.assertEqual(len(result), 0)

    def test_get_attribute_error(self):
        session = AlchemyMagicMock()
        with self.assertRaises(AttributeError):
            session.query(Tag).filter(Tag.foo == 1).all()

    def test_get_all(self):
        session = UnifiedAlchemyMagicMock()
        session.add(Tag(id=1, name='a', added_by='user'))
        result = session.query(Tag).all()
        return self.assertEqual(len(result), 1)
