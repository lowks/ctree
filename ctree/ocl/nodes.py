"""
OpenCL nodes supported by ctree.
"""

class OclNode(CAstNode):
  """Base class for all OpenCL nodes supported by ctree."""
  def codegen(self, indent=0):
    from ctree.ocl.codegen import OclCodeGen
    return OclCodeGen(indent).visit(self)

  def dotgen(self, indent=0):
    from ctree.ocl.dotgen import OclDotGen
    return OclDotGen().visit(self)
