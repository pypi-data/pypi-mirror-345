import blsct
from ...scalar_based_key import ScalarBasedKey

class SpendingKey(ScalarBasedKey):
  """
  Represents a spending key. A spending key is a Scalar and introduces no new functionality; it serves purely as a semantic alias.

  >>> from blsct import SpendingKey
  >>> SpendingKey()
  <blsct.keys.child_key_desc.tx_key_desc.spending_key.SpendingKey object at 0x10102a660>  # doctest: +SKIP
  """
  pass
 
