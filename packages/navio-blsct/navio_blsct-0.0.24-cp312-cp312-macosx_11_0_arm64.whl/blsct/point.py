import blsct
from .managed_obj import ManagedObj
from typing import Any, Self, override

class Point(ManagedObj):
  """
  Represents an element in the BLS12-381 G1 curve group.
  A wrapper of MclG1Point_ in navio-core.

  .. _MclG1Point: https://github.com/nav-io/navio-core/blob/master/src/blsct/arith/mcl/mcl_g1point.h

  Instantiating a Point object without a parameter returns the base point of the BLS12-381 G1 curve.

  >>> from blsct import Point
  >>> a = Point()
  >>> b = Point.base_point()
  >>> a.to_hex()
  '1 17f1d3a73197d7942695638c4fa9ac0fc3688c4f9774b905a14e3a3f171bac586c55e83ff97a1aeffb3af00adb22c6bb 8b3f481e3aaa0f1a09e30ed741d8ae4fcf5e095d5d00af600db18cb2c04b3edd03cc744a2888ae40caa232946c5e7e1'
  >>> b.to_hex()
  '1 17f1d3a73197d7942695638c4fa9ac0fc3688c4f9774b905a14e3a3f171bac586c55e83ff97a1aeffb3af00adb22c6bb 8b3f481e3aaa0f1a09e30ed741d8ae4fcf5e095d5d00af600db18cb2c04b3edd03cc744a2888ae40caa232946c5e7e1'
  >>> a.to_hex() == b.to_hex()
  True
  >>> a.is_valid()
  True
  >>> Point.random().to_hex()
  '1 124c3c9dc6eb46cf8bcddc64559c05717d49730c9e474230dfd75e76c7ac07f954bfcf60432a9175d1eb0d54e502301b 2cbaf63a39d601edfd07df64de8c67059cc40a340da2ef1621d680014906d6409a55e4db08ebf32ba581e98d640e4a8'  # doctest: +SKIP
  """

  @staticmethod
  def random() -> Self:
    """Generate a random point"""
    rv = blsct.gen_random_point()
    point = Point.from_obj(rv.value)
    blsct.free_obj(rv)
    return point

  @staticmethod
  def base() -> Self:
    """Get the base point of the BLS12-381 G1 curve"""
    rv = blsct.gen_base_point()
    point = Point.from_obj(rv.value)
    blsct.free_obj(rv)
    return point

  def is_valid(self) -> bool:
    """Check if the point is valid"""
    return blsct.is_valid_point(self.value())

  def to_hex(self) -> str:
    """Convert the point to a hexadecimal string"""
    return blsct.point_to_hex(self.value())

  @override
  def value(self) -> Any:
    return blsct.cast_to_point(self.obj)

  @classmethod
  def default_obj(cls) -> Any:
    rv = blsct.gen_base_point()
    return rv.value 
 
