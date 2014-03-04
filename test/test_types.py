import unittest

from ctree.c.nodes import *
from ctree.c.types import *

class TestTypeProperties(unittest.TestCase):
  def test_float_equality(self):
    self.assertEqual(Float(), Float())

  def test_unequality(self):
    self.assertNotEqual(Float(), Int())


class TestTypeFetcher(unittest.TestCase):
  def _check(self, actual, expected):
    self.assertEqual(actual, expected)

  def test_string_type(self):
    s = String("foo")
    self._check(s.get_type(), Ptr(Char()))

  def test_int_type(self):
    n = Constant(123)
    self._check(n.get_type(), Long())

  def test_float_type(self):
    n = Constant(123.4)
    self._check(n.get_type(), Double())

  def test_char_type(self):
    n = Constant('b')
    self._check(n.get_type(), Char())

  def test_binop_add_intint(self):
    a, b = Constant(1), Constant(2)
    node = Add(a, b)
    self._check(node.get_type(), Long())

  def test_binop_add_floatfloat(self):
    a, b = Constant(1.3), Constant(2.4)
    node = Add(a, b)
    self._check(node.get_type(), Double())

  def test_binop_add_floatint(self):
    a, b = Constant(1.3), Constant(2)
    node = Add(a, b)
    self._check(node.get_type(), Double())

  def test_binop_add_intfloat(self):
    a, b = Constant(1), Constant(2.3)
    node = Add(a, b)
    self._check(node.get_type(), Double())

  def test_binop_add_charint(self):
    a, b = Constant('b'), Constant(2)
    node = Add(a, b)
    self._check(node.get_type(), Long())

  def test_binop_add_charfloat(self):
    a, b = Constant('b'), Constant(2.3)
    node = Add(a, b)
    self._check(node.get_type(), Double())

  def test_binop_compare(self):
    a, b = Constant('b'), Constant(2.3)
    node = Lt(a, b)
    self._check(node.get_type(), Int())

  def test_binop_compare(self):
    a, b = Constant('b'), Constant(2.3)
    node = Comma(a, b)
    self._check(node.get_type(), Double())

  def test_bad_constant(self):
    class nothing: pass
    a = Constant(nothing())
    with self.assertRaises(Exception):
      self._check(a.get_type(), Int())

  class Nothing:
    pass

  def test_bad_type_coversion(self):
    with self.assertRaises(Exception):
      get_ctree_type(self.Nothing)

  def test_bad_obj_coversion(self):
    with self.assertRaises(Exception):
      get_ctree_type(self.Nothing())
