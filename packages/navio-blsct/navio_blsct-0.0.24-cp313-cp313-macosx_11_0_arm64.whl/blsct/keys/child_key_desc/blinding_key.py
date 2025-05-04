import blsct
from ..scalar_based_key import ScalarBasedKey
from typing import Any

class BlindingKey(ScalarBasedKey):
  """
  Represents a blinding key. A blinding key is a Scalar and introduces no new functionality; it serves purely as a semantic alias.

  >>> from blsct import BlindingKey
  >>> BlindingKey()
  <blsct.keys.child_key_desc.blinding_key.BlindingKey object at 0x10102a660>  # doctest: +SKIP
  """
  pass
 
