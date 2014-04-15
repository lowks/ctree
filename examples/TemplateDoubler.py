"""
Parses the python AST below, transforms it to C, JITs it, and runs it.
"""

import logging

logging.basicConfig(level=20)

import numpy as np

from ctree.frontend import get_ast
from ctree.c.nodes import *
from ctree.c.types import *
from ctree.templates.nodes import *
from ctree.transformations import *
from ctree.jit import LazySpecializedFunction
from ctree.types import get_ctree_type

# ---------------------------------------------------------------------------
# Specializer code


class OpTranslator(LazySpecializedFunction):
    def args_to_subconfig(self, args):
        """
        Analyze arguments and return a 'subconfig', a hashable object
        that classifies them. Arguments with identical subconfigs
        might be processed by the same generated code.
        """
        A = args[0]
        return {
            'A_len':   len(A),
            'A_dtype': A.dtype,
            'A_ndim':  A.ndim,
            'A_shape': A.shape,
        }

    def transform(self, py_ast, program_config):
        """
        Convert the Python AST to a C AST according to the directions
        given in program_config.
        """
        arg_config, tuner_config = program_config
        len_A   = arg_config['A_len']
        A_dtype = arg_config['A_dtype']
        A_ndim  = arg_config['A_ndim']
        A_shape = arg_config['A_shape']

        inner_type = get_ctree_type(A_dtype)
        array_type = NdPointer(A_dtype, A_ndim, A_shape)
        apply_one_typesig = FuncType(inner_type, [inner_type])

        template_entries = {
            'array_decl': SymbolRef("A", array_type),
            'array_ref' : SymbolRef("A"),
            'num_items' : Constant(len_A),
        }

        tree = CFile("generated", [
            py_ast.body[0],
            StringTemplate("""\
            void apply_all($array_decl) {
                for (int i = 0; i < $num_items; i++) {
                    $array_ref[i] = apply( $array_ref[i] );
                }
            }
            """, template_entries)
        ])

        tree = PyBasicConversions().visit(tree)

        apply_one = tree.find(FunctionDecl, name="apply")
        apply_one.set_static().set_inline()
        apply_one.set_typesig(apply_one_typesig)

        with open("graph.dot", 'w') as f:
            f.write( tree.to_dot() )

        entry_point_typesig = FuncType(Void(), [array_type]).as_ctype()
        return Project([tree]), entry_point_typesig


class ArrayOp(object):
    """
    A class for managing independent operation on elements
    in numpy arrays.
    """

    def __init__(self):
        """Instantiate translator."""
        self.c_apply_all = OpTranslator(get_ast(self.apply), "apply_all")

    def __call__(self, A):
        """Apply the operator to the arguments via a generated function."""
        return self.c_apply_all(A)


# ---------------------------------------------------------------------------
# User code

class Doubler(ArrayOp):
    """Double elements of the array."""

    def apply(n):
        return n * 2


def py_doubler(A):
    A *= 2


def main():
    c_doubler = Doubler()

    # doubling doubles
    actual_d = np.ones(12, dtype=np.float64)
    expected_d = np.ones(12, dtype=np.float64)
    c_doubler(actual_d)
    py_doubler(expected_d)
    np.testing.assert_array_equal(actual_d, expected_d)

    # doubling floats
    actual_f = np.ones(13, dtype=np.float32)
    expected_f = np.ones(13, dtype=np.float32)
    c_doubler(actual_f)
    py_doubler(expected_f)
    np.testing.assert_array_equal(actual_f, expected_f)

    # doubling ints
    actual_i = np.ones(14, dtype=np.int32)
    expected_i = np.ones(14, dtype=np.int32)
    c_doubler(actual_i)
    py_doubler(expected_i)
    np.testing.assert_array_equal(actual_i, expected_i)

    # demonstrate caching
    c_doubler(actual_i)
    c_doubler(actual_i)
    py_doubler(expected_i)
    py_doubler(expected_i)
    np.testing.assert_array_equal(actual_i, expected_i)

    print("Success.")


if __name__ == '__main__':
    main()
