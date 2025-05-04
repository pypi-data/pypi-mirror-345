import blsct
from .managed_obj import ManagedObj
from typing import Any, Self, override

class TxId(ManagedObj):
  """
  Represents the transaction ID of a confidential transaction.

  >>> from blsct import TxId, TX_ID_SIZE
  >>> import secrets
  >>> hex = secrets.token_hex(TX_ID_SIZE)
  >>> tx_id = TxId.from_hex(hex)
  >>> tx_id.to_hex()
  'f60b407e98916361594ecd53d7bed716fb901570815c323244da8d4189833df3'  # doctest: +SKIP
  """
  def to_hex(self) -> str:
    """Convert the TxId to a hexadecimal string."""
    buf = blsct.cast_to_uint8_t_ptr(self.value())
    return blsct.to_hex(buf, blsct.TX_ID_SIZE)

  def from_hex(hex) -> Any:
    """Create a TxId from a hexadecimal string."""
    if len(hex) != blsct.TX_ID_SIZE * 2:
      raise ValueError(f"Invlid TxId hex length. Expected {blsct.TX_ID_SIZE * 2}, but got {len(hex)}.")
    obj = blsct.hex_to_malloced_buf(hex) 
    return TxId(obj)

  @override
  def value(self):
    return blsct.cast_to_uint8_t_ptr(self.obj)

  @classmethod
  def default_obj(cls) -> Any:
    raise NotImplementedError("Cannot create a TxId without required parameters.")

