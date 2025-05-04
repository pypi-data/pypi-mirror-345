import blsct
from .managed_obj import ManagedObj
from typing import Any, Self, override

class SubAddrId(ManagedObj):
  """
  Represents a sub-address ID.

  >>> from blsct import SubAddrId
  >>> SubAddrId.generate(123, 456)
  <blsct.sub_addr_id.SubAddrId object at 0x1050d4ad0>  # doctest: +SKIP
  """
  @staticmethod
  def generate(
    account: int,
    address: int
  ) -> Self:
    """Generate a sub-address ID from an account and an address"""
    obj = blsct.gen_sub_addr_id(account, address);
    return SubAddrId(obj)

  @override
  def value(self) -> Any:
    return blsct.cast_to_sub_addr_id(self.obj)

  @override
  def default_obj(self) -> Self:
    raise NotImplementedError(f"Cannot create a SubAddrId without required parameters.")

