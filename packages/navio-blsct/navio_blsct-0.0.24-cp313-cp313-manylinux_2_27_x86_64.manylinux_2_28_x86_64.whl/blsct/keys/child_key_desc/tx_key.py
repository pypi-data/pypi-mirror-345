import blsct
from ..scalar_based_key import ScalarBasedKey
from .tx_key_desc.spending_key import SpendingKey
from .tx_key_desc.view_key import ViewKey
from typing import Any

class TxKey(ScalarBasedKey):
  """
  Represents a tx key. A tx key is a Scalar and introduces no new functionality; it serves purely as a semantic alias. Both SpendingKey and ViewKey are exclusively derived from a TxKey.

  >>> from blsct import TxKey
  >>> k = TxKey()
  >>> k.to_spending_key()
  <blsct.keys.child_key_desc.tx_key_desc.spending_key.SpendingKey object at 0x10109c7d0>  # doctest: +SKIP
  >>> k.to_view_key()
  <blsct.keys.child_key_desc.tx_key_desc.view_key.ViewKey object at 0x10109ca50>  # doctest: +SKIP
  """
  def to_spending_key(self) -> SpendingKey:
    """derive a spending key from the tx key"""
    obj = blsct.from_tx_key_to_spending_key(self.value())
    return SpendingKey(obj)

  def to_view_key(self) -> ViewKey:
    """derive a view key from the tx key"""
    obj = blsct.from_tx_key_to_view_key(self.value())
    return ViewKey(obj)

