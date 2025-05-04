import blsct
from ..scalar_based_key import ScalarBasedKey
from typing import Any

class TokenKey(ScalarBasedKey):
  """
  Represents a token key. A token key is a Scalar and introduces no new functionality; it serves purely as a semantic alias.

  >>> from blsct import TokenKey
  >>> TokenKey()
  <blsct.keys.child_key_desc.token_key.TokenKey object at 0x101028ad0>  # doctest: +SKIP
  """
  pass
 

