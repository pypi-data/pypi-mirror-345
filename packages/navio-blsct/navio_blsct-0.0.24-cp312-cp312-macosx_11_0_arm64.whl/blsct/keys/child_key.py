import blsct
from ..scalar import Scalar
from .scalar_based_key import ScalarBasedKey
from .child_key_desc.blinding_key import BlindingKey
from .child_key_desc.token_key import TokenKey
from .child_key_desc.tx_key import TxKey
from typing import Any, Self, override

class ChildKey(ScalarBasedKey):
  """
  Represents a child key. A child key is a Scalar and introduces no new functionality; it serves purely as a semantic alias. BlindingKey, TokenKey and TxKey are exclusively derived from a ChildKey.

  >>> from blsct import ChildKey, Scalar
  >>> ChildKey()
  <blsct.keys.child_key.ChildKey object at 0x101028ad0>  # doctest: +SKIP
  >>> s = Scalar()
  >>> k = ChildKey.from_scalar(s)
  >>> k.to_blinding_key()
  <blsct.keys.child_key_desc.blinding_key.BlindingKey object at 0x10109c7d0>  # doctest: +SKIP
  >>> k.to_token_key()
  <blsct.keys.child_key_desc.token_key.TokenKey object at 0x10109c550>  # doctest: +SKIP
  >>> k.to_tx_key()
  <blsct.keys.child_key_desc.tx_key.TxKey object at 0x10109c190>  # doctest: +SKIP
  """
  @staticmethod
  def from_scalar(seed: Scalar) -> Self:
    """create a child key from a scalar"""
    obj = blsct.from_seed_to_child_key(seed.value())
    return ChildKey(obj)

  def to_blinding_key(self) -> BlindingKey:
    """derive a blinding key from the child key"""
    obj = blsct.from_child_key_to_blinding_key(self.value())
    return BlindingKey(obj)

  def to_token_key(self) -> TokenKey:
    """derive a token key from the child key"""
    obj = blsct.from_child_key_to_token_key(self.value())
    return TokenKey(obj)

  def to_tx_key(self) -> TxKey:
    """derive a tx key from the child key"""
    obj = blsct.from_child_key_to_tx_key(self.value())
    return TxKey(obj)

