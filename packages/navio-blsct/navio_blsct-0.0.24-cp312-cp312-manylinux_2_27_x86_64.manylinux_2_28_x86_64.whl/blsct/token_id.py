import blsct
from .managed_obj import ManagedObj
from typing import Any, Self, override

class TokenId(ManagedObj):
  """
  Represents a token ID. A token ID consists of two parameters: token and subid, both of which are optional. When omitted, default values are used instead of random values.

  >>> from blsct import TokenId
  >>> TokenId()
  <blsct.token_id.TokenId object at 0x105a00ad0>  # doctest: +SKIP
  >>> TokenId.from_token(123)
  <blsct.token_id.TokenId object at 0x105a8c050>  # doctest: +SKIP
  >>> token_id = TokenId.from_token_and_subid(123, 456)
  >>> token_id.token()
  123
  >>> token_id.subid()
  456
  """
  @staticmethod
  def from_token(token: int) -> Self:
    """Generate a token ID from a given token."""
    rv = blsct.gen_token_id(token);
    token_id = TokenId(rv.value)
    blsct.free_obj(rv)
    return token_id
 
  @staticmethod
  def from_token_and_subid(token: int, subid: int) -> Self:
    """Generate a token ID from a given token and subid."""
    rv = blsct.gen_token_id_with_subid(token, subid) 
    token_id = TokenId(rv.value)
    blsct.free_obj(rv)
    return token_id

  def token(self) -> int:
    """Get the token from the token ID."""
    return blsct.get_token_id_token(self.value())

  def subid(self) -> int:
    """Get the subid from the token ID."""
    return blsct.get_token_id_subid(self.value())

  @override
  def value(self):
    return blsct.cast_to_token_id(self.obj)

  @classmethod
  def default_obj(cls) -> Any:
    rv = blsct.gen_default_token_id()
    return rv.value

