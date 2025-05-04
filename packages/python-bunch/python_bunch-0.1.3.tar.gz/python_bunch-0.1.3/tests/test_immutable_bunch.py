import json
import unittest
from collections import Counter
from contextlib import contextmanager

from bunch.immutable_bunch import ImmutableBunch, ImmutableBunchException


@contextmanager
def raise_immutable_exception():
    try:
        yield
    except ImmutableBunchException:
        pass
    else:
        raise Exception('ImmutableBunchException not raised as expected')


class TestBunch(unittest.TestCase):
    def test_getitem(self):
        ib = ImmutableBunch(name='Alice', age=30)
        self.assertEqual(ib['name'], 'Alice')

    def test_setitem(self):
        ib = ImmutableBunch(name='Alice')
        with raise_immutable_exception():
            ib['age'] = 30

    def test_delitem(self):
        ib = ImmutableBunch(name='Alice', age=30)
        with raise_immutable_exception():
            del ib['name']

    def test_contains(self):
        ib = ImmutableBunch(name='Alice', age=30)
        self.assertTrue('name' in ib)
        self.assertFalse('location' in ib)

    def test_str(self):
        ib = ImmutableBunch(name='Alice', age=30)
        expected_str = json.dumps({'name': 'Alice', 'age': 30})
        self.assertEqual(ib.__str__(), expected_str)

    def test_repr(self):
        ib = ImmutableBunch(name='Alice', age=30)
        expected_repr = json.dumps({'name': 'Alice', 'age': 30})
        self.assertEqual(ib.__repr__(), expected_repr)

    def test_getattr(self):
        ib = ImmutableBunch(name='Alice', age=30)
        self.assertEqual(ib.age, 30)

    def test_setattr(self):
        ib = ImmutableBunch(name='Alice', age=30)
        with raise_immutable_exception():
            ib.age = 40

    def test_delattr(self):
        ib = ImmutableBunch(name='Alice', age=30)
        with raise_immutable_exception():
            del ib.age

    def test_contains_value(self):
        ib = ImmutableBunch(name='Alice', age=30)
        self.assertTrue(ib.contains_value('Alice'))
        self.assertFalse(ib.contains_value('Bob'))

    def test_clear(self):
        ib = ImmutableBunch(name='Alice', age=30)
        with raise_immutable_exception():
            ib.clear()

    def test_pop(self):
        ib = ImmutableBunch(name='Alice', age=30)
        with raise_immutable_exception():
            ib.pop('name')

    def test_popitem(self):
        ib = ImmutableBunch(name='Alice', age=30)
        with raise_immutable_exception():
            ib.popitem()

    def test_update(self):
        ib = ImmutableBunch(name='Alice', age=30)
        d = {'name': 'Bob', 'age': 35}
        with raise_immutable_exception():
            ib.update(d)

    def test_setdefault(self):
        ib = ImmutableBunch(name='Alice', age=30)
        with raise_immutable_exception():
            ib.setdefault('location')

    def test_keys(self):
        ib = ImmutableBunch(name='Alice', age=30)
        self.assertEqual(Counter(ib.keys()), Counter(['name', 'age']))

    def test_values(self):
        ib = ImmutableBunch(name='Alice', age=30)
        self.assertEqual(Counter(ib.values()), Counter(['Alice', 30]))

    def test_items(self):
        ib = ImmutableBunch(name='Alice', age=30)
        self.assertEqual(Counter(ib.items()), Counter([('name', 'Alice'), ('age', 30)]))

    def test_from_dict(self):
        data = {'fruit': 'apple', 'color': 'red'}
        ib = ImmutableBunch.from_dict(data)
        self.assertEqual(ib.fruit, 'apple')
        self.assertEqual(ib.color, 'red')


if __name__ == '__main__':
    unittest.main()
