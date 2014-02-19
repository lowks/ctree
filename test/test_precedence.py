import unittest

from ctree.nodes import *

class TestPrecedence(unittest.TestCase):

  def setUp(self):
    self.args = (SymbolRef('a'), SymbolRef('b'), SymbolRef('c'))

  def _check(self, tree, expected):
    actual = str(tree)
    self.assertEqual(actual, expected)

  def test_addmul_rhs(self):
    a, b, c = self.args
    tree = Add(a, Mul(b, c))
    self._check(tree, "a + b * c")

  def test_addmul_lhs(self):
    a, b, c = self.args
    tree = Add(Mul(a, b), c)
    self._check(tree, "a * b + c")

  @unittest.skip("pending precedence handler")
  def test_muladd_rhs(self):
    a, b, c = self.args
    tree = Mul(a, Add(b, c))
    self._check(tree, "a * (b + c)")

  @unittest.skip("pending precedence handler")
  def test_muladd_lhs(self):
    a, b, c = self.args
    tree = Mul(Add(a, b), c)
    self._check(tree, "(a + b) * c")
