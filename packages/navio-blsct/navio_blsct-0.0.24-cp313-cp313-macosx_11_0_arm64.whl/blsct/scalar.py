import blsct
from .managed_obj import ManagedObj
from typing import Any, Optional, override, Self

class Scalar(ManagedObj):
  """
  Represents an element of the finite field :math:`\mathbb{F}_r`, where :math:`r` is the order of the generator point of the BLS12-381 G1 group.

  A wrapper of MclScalar_ in navio-core.

  .. _MclScalar: https://github.com/nav-io/navio-core/blob/master/src/blsct/arith/mcl/mcl_scalar.h

  Instantiating a Scalar without a parameter is equivalent to calling Scalar.random().

  >>> from blsct import Scalar
  >>> a = Scalar(123)
  >>> a.to_int()
  123
  >>> a.to_hex()
  '7b'
  >>> b = Scalar.random()
  >>> b.to_hex()  # doctest: +SKIP
  '2afe6b2a5222bf5768ddbdbe3e5ea71e964d5312a2761a165395ad231b710edd'
  >>> Scalar().to_hex()
  '5e6efdcf00ce467de29a970adf3a09f8c93e51dc7f1405bbe9dffeeabf952fbe'
  >>> Scalar.zero().to_hex()
  '0'
  """
  def __init__(self, value: Optional[int] = None):
    if isinstance(value, int):
      rv = blsct.gen_scalar(value)
      super().__init__(rv.value)
    elif value is None:
      super().__init__()
    elif isinstance(value, object):
      super().__init__(value)
    else:
      raise ValueError(f"Scalar can only be instantiated with int, but got '{type(value).__name__}'")

  @staticmethod
  def random() -> Self:
    """Generate a random scalar"""
    rv = blsct.gen_random_scalar()
    scalar = Scalar(rv.value)
    blsct.free_obj(rv)
    return scalar

  def to_hex(self) -> str:
    """Convert the scalar to a hexadecimal string"""
    return blsct.scalar_to_hex(self.value())

  def to_int(self) -> int:
    """Convert the scalar to an integer"""
    return  blsct.scalar_to_uint64(self.value())

  def zero() -> Self:
    """Return a zero scalar"""
    return Scalar(0)

  @override
  def value(self) -> Any:
    return blsct.cast_to_scalar(self.obj)

  @classmethod
  def default_obj(cls) -> Any:
    rv = blsct.gen_random_scalar()
    value = rv.value
    blsct.free_obj(rv)
    return value

