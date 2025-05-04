import blsct
from ..managed_obj import ManagedObj
from ..scalar import Scalar
from .child_key_desc.tx_key_desc.view_key import ViewKey
from typing import Any, Self, override

class PublicKey(ManagedObj):
  """
  Represents an element in the BLS12-381 G1 curve group that is used as a public key.

  >>> from blsct import PublicKey, Scalar, ViewKey
  >>> s = Scalar.random()
  >>> PublicKey.from_scalar(s)
  <blsct.keys.public_key.PublicKey object at 0x100bbfd90>  # doctest: +SKIP
  >>> PublicKey.random()
  <blsct.keys.public_key.PublicKey object at 0x1013f4190>  # doctest: +SKIP
  >>> pk = PublicKey.random()
  >>> vk = ViewKey()
  >>> PublicKey.generate_nonce(pk, vk)
  <blsct.keys.public_key.PublicKey object at 0x10100f950>  # doctest: +SKIP
  """

  @staticmethod
  def random() -> Self:
    """Get a random public key"""
    rv = blsct.gen_random_public_key()
    pk = PublicKey(rv.value)
    blsct.free_obj(rv)
    return pk

  @staticmethod
  def from_scalar(scalar: Scalar) -> Self:
    """Convert a scalar to a public key"""
    blsct_pub_key = blsct.scalar_to_pub_key(scalar.value())
    return PublicKey(blsct_pub_key)

  @staticmethod
  def generate_nonce(
    blinding_pub_key: Self,
    view_key: ViewKey
  ) -> Self:
   """Generate a nonce PublicKey from blinding public key and view key"""
   blsct_nonce = blsct.calc_nonce(
     blinding_pub_key.value(),
     view_key.value()
   )
   return PublicKey(blsct_nonce)

  @override
  def value(self):
    return blsct.cast_to_pub_key(self.obj)

  @classmethod
  def default_obj(cls) -> Any:
    rv = blsct.gen_random_public_key()
    return rv.value

