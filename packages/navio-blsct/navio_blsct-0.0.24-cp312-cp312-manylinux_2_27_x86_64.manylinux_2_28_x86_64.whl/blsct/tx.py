import blsct
from .managed_obj import ManagedObj
from .tx_id import TxId
from .tx_in import TxIn
from .tx_out import TxOut
from typing import Any, Self, override

# stores serialized tx represented as uint8_t*
class Tx(ManagedObj):
  """
  Represents a confidential transaction.

  >>> from blsct import ChildKey, DoublePublicKey, OutPoint, PublicKey, SpendingKey, SubAddr, SubAddrId, TokenId, TX_ID_SIZE, Tx, TxId, TxIn, TxOut
  >>> import secrets
  >>> num_tx_in = 1
  >>> num_tx_out = 1
  >>> default_fee = 200000
  >>> fee = (num_tx_in + num_tx_out) * default_fee
  >>> out_amount = 10000
  >>> in_amount = fee + out_amount
  >>> tx_id = TxId.from_hex(secrets.token_hex(32))
  >>> out_index = 0
  >>> out_point = OutPoint.generate(tx_id, out_index)
  >>> gamma = 100
  >>> spending_key = SpendingKey()
  >>> token_id = TokenId()
  >>> tx_in = TxIn.generate(in_amount, gamma, spending_key, token_id, out_point)
  >>> sub_addr = SubAddr.from_double_public_key(DoublePublicKey())
  >>> tx_out = TxOut.generate(sub_addr, out_amount, 'navio')
  >>> tx = Tx.generate([tx_in], [tx_out])
  >>> for tx_in in tx.get_tx_ins(): 
  ...   print(f"prev_out_hash: {tx_in.get_prev_out_hash()}")
  ...   print(f"prev_out_n: {tx_in.get_prev_out_n()}")
  ...   print(f"script_sig: {tx_in.get_script_sig().to_hex()}")
  ...   print(f"sequence: {tx_in.get_sequence()}")
  ...   print(f"script_witness: {tx_in.get_script_witness().to_hex()}")
  ...   
  prev_out_hash: TxId(b1166eabed80a211639e07c9382b905706123e51f35088d7b9ccfb768161adce)  # doctest: +SKIP
  prev_out_n: 0  # doctest: +SKIP
  script_sig: 00000000000000000000000000000000000000000000000000000000  # doctest: +SKIP
  sequence: 4294967295  # doctest: +SKIP
  script_witness: 00000000000000000000000000000000000000000000000000000000  # doctest: +SKIP
  >>> for tx_out in tx.get_tx_outs():
  ...   print(f"value: {tx_out.get_value()}")
  ...   print(f"script_pub_key: {tx_out.get_script_pub_key().to_hex()}")
  ...   print(f"token_id: token={tx_out.get_token_id().token()}, subid={tx_out.get_token_id().subid()}")
  ...   print(f"spending_key: {tx_out.get_spending_key()}")
  ...   print(f"ephemeral_key: {tx_out.get_ephemeral_key()}")
  ...   print(f"blinding_key: {tx_out.get_blinding_key()}")
  ...   print(f"view_tag: {tx_out.get_view_tag()}")
  ...   print(f"range_proof.A: {tx_out.get_range_proof_A().to_hex()}")
  ...   print(f"range_proof.B: {tx_out.get_range_proof_B().to_hex()}")
  ...   print(f"range_Proof.r_prime: {tx_out.get_range_proof_r_prime()}")
  ...   print(f"range_proof.s_prime: {tx_out.get_range_proof_s_prime()}")
  ...   print(f"range_proof.delta_prime: {tx_out.get_range_proof_delta_prime()}")
  ...   print(f"range_proof.alpha_hat: {tx_out.get_range_proof_alpha_hat()}")
  ...   print(f"range_proof.tau_x: {tx_out.get_range_proof_tau_x()}")
  ...   
  value: 0  # doctest: +SKIP
  script_pub_key: 51000000000000000000000000000000000000000000000000000000  # doctest: +SKIP
  token_id: token=0, subid=18446744073709551615  # doctest: +SKIP
  spending_key: Point(1 43c0386c950f8298bd2a6416dfb2696f08e155a76227f789eff0a78d8a7d0c1926b8b5de97818bff168917e8dec199d 170cdcb9cfc862168dfbfc52dea568ef38b2bdd424e17a7e5ebf72205c7e1c6a9783ee5e2719a77d684f1e3d1ee90cd)  # doctest: +SKIP
  ephemeral_key: Point(1 dbb54183f593cbb325c258a2f506feda30938d7ac5135e70fd695f596a8401a965c79b1d86c99bd935a9bdf7d0f7d63 19c3fb04fb219dedd2d0b328127edfc32de671874ed37db578f8c35a20215245abced2f511dd613a3a6bec06c892c43)  # doctest: +SKIP
  blinding_key: Point(1 11bfe37be891928ac997a4713ed23b20a4754c9acc59a223141637b31b6b478e1e5e3566ae2f57098199bdfaa2e0347a 5a88b4430f2e6bb3e066e97448e5246494e4057f7162dbabdee67018c56e5d46e88c91f1279662a5466b0cb09d557f)  # doctest: +SKIP
  view_tag: 43421  # doctest: +SKIP
  range_proof.A: 1 d1a9ece6622f7e9b1e4538ebadf8586054507823a8bf6752e30ac808963da12abcd0658351691197de6f0b1631723bf 72ed6a826f0c81bd803f55c64aed35b3dee639ef5f9023d73184ca05cc27f87b67374b1ead95dedb28ed6133e97c42  # doctest: +SKIP
  range_proof.B: 1 7f5c8c20c84286b59554aa4baeba056f97b69a4deb79bb646461bb6b69109a7888d6c28f457f95859e3cd14de30eea7 b22e8d359cdf4e9aa66579f94017aba1a4fcd146364f7555a5c97c5df33eb61583a9882469edd30555be5f67ea05ad  # doctest: +SKIP
  range_Proof.r_prime: Point(0)  # doctest: +SKIP
  range_proof.s_prime: Point(0)  # doctest: +SKIP
  range_proof.delta_prime: Point(0)  # doctest: +SKIP
  range_proof.alpha_hat: Point(0)  # doctest: +SKIP
  range_proof.tau_x: Scalar(707fe053abde7620ba50206b52c94f57d8301a70230c97fb0c9bbc10f6660a18)  # doctest: +SKIP
  value: 0  # doctest: +SKIP
  script_pub_key: 51000000000000000000000000000000000000000000000000000000  # doctest: +SKIP
  token_id: token=0, subid=18446744073709551615  # doctest: +SKIP
  spending_key: Point(1 187232c232f64c69aabdcc972fa53ee6348070dd95485d87e83381c51bf3390342473c27308293d2abe5f43660e38e5d 4768f24b50c7865c795231319d5347dbf60e5bbb3e317ef421d31a1893ef917647865fd4d12fdb8794f9a011b61cf7)  # doctest: +SKIP
  ephemeral_key: Point(1 f307fb2f34626f0da7af6bba99616eb3156d298ecbbda78551dbdb50a1e5fcdc171970ed07df01bcedacb4b56d606da be1c4985d574bca1a46f49e181144428e8ab22e2d33ada48720d6c307c97d1abc49a6a624b0db33f215766af2458d5)  # doctest: +SKIP
  blinding_key: Point(0)  # doctest: +SKIP
  view_tag: 21881  # doctest: +SKIP
  range_proof.A: 1 731fba528d2461adc510c2cea6538cb4c31869448ee04f83665aa24a83c6a79aff088893d908ad7df4236e8c10a7ed1 7f2fd4146dc6cf5e25f1e7334d364cf2463505e2c772e66ba7ecfcd7970ff8d38a7e3fa943adaacebeb336a9d21b76  # doctest: +SKIP
  range_proof.B: 1 af830e83f6438cc9bdcc52be4d43f09b330f849b6c61a825d003748716ef59b51904dc482f65ce6609bc90ed06ccb90 17c2b3479186582f7e831c2b62b2f2adadb38bd76f7a87ab6da34f2639d267d1567c6d24f2a67ae991291261abe3416  # doctest: +SKIP
  range_Proof.r_prime: Point(0)  # doctest: +SKIP
  range_proof.s_prime: Point(0)  # doctest: +SKIP
  range_proof.delta_prime: Point(0)  # doctest: +SKIP
  range_proof.alpha_hat: Point(0)  # doctest: +SKIP
  range_proof.tau_x: Scalar(4193251795eaf35243e68c9fef5dd7cafd3c34bcc0422c5c5b8f825c56767546)  # doctest: +SKIP
  value: 292125  # doctest: +SKIP
  script_pub_key: 6a000000000000000000000000000000000000000000000000000000  # doctest: +SKIP
  token_id: token=0, subid=18446744073709551615  # doctest: +SKIP
  spending_key: Point(0)  # doctest: +SKIP
  ephemeral_key: Point(0)  # doctest: +SKIP
  blinding_key: Point(0)  # doctest: +SKIP
  view_tag: 0  # doctest: +SKIP
  range_proof.A: 0  # doctest: +SKIP
  range_proof.B: 0  # doctest: +SKIP
  range_Proof.r_prime: Point(0)  # doctest: +SKIP
  range_proof.s_prime: Point(0)  # doctest: +SKIP
  range_proof.delta_prime: Point(0)  # doctest: +SKIP
  range_proof.alpha_hat: Point(0)  # doctest: +SKIP
  range_proof.tau_x: Scalar(0)  # doctest: +SKIP
  >>> ser_tx = tx.serialize()
  >>> tx.deserialize(ser_tx)
  Tx(<swig object of type 'unsigned char *' at 0x102529080>)  # doctest: +SKIP
  """
  @staticmethod
  def generate(
    tx_ins: list[TxIn],
    tx_outs: list[TxOut]
  ) -> Self:
    """generate a confidential transaction from a list of inputs and outputs."""

    tx_in_vec = blsct.create_tx_in_vec()
    for tx_in in tx_ins:
      blsct.add_tx_in_to_vec(tx_in_vec, tx_in.value())

    tx_out_vec = blsct.create_tx_out_vec()
    for tx_out in tx_outs:
      blsct.add_tx_out_to_vec(tx_out_vec, tx_out.value())

    rv = blsct.build_tx(tx_in_vec, tx_out_vec)

    if rv.result == blsct.BLSCT_IN_AMOUNT_ERROR:
      blsct.free_obj(rv)
      raise ValueError(f"Failed to build transaction. tx_ins[{rv.in_amount_err_index}] has an invalid amount")


    if rv.result == blsct.BLSCT_OUT_AMOUNT_ERROR:
      blsct.free_obj(rv)
      raise ValueError(f"Failed to build transaciton. tx_outs[{rv.out_amount_err_index}] has an invalid amount")

    if rv.result != 0:
      blsct.free_obj(rv)
      raise valueerror(f"building tx failed: {rv.result}")

    obj = Tx(rv.ser_tx)
    obj.obj_size = rv.ser_tx_size
    blsct.free_obj(rv)
    return obj

  def get_tx_id(self) -> TxId:
    """Get the transaction ID."""
    tmp_tx = blsct.deserialize_tx(self.value(), self.obj_size)
    tx_id_hex = blsct.get_tx_id(tmp_tx)
    blsct.free_obj(tmp_tx)
    return TxId.from_hex(tx_id_hex)

  def get_tx_ins(self) -> list[TxIn]:
    """Get the transaction inputs."""
    # returns cmutabletransaction*
    blsct_tx = blsct.deserialize_tx(self.value(), self.obj_size)

    blsct_tx_ins = blsct.get_tx_ins(blsct_tx)
    tx_ins_size = blsct.get_tx_ins_size(blsct_tx_ins)

    tx_ins = []
    for i in range(tx_ins_size):
      rv = blsct.get_tx_in(blsct_tx_ins, i)
      tx_in = TxIn(rv.value)
      tx_ins.append(tx_in)
      blsct.free_obj(rv)
    blsct.free_obj(blsct_tx)

    return tx_ins

  def get_tx_outs(self) -> list[TxOut]:
    """Get the transaction outputs."""
    # returns cmutabletransaction*
    blsct_tx = blsct.deserialize_tx(self.value(), self.obj_size)

    blsct_tx_outs = blsct.get_tx_outs(blsct_tx)
    tx_outs_size = blsct.get_tx_outs_size(blsct_tx_outs)

    tx_outs = []
    for i in range(tx_outs_size):
      rv = blsct.get_tx_out(blsct_tx_outs, i)
      tx_out = TxOut(rv.value)
      tx_outs.append(tx_out)
      blsct.free_obj(rv)
    blsct.free_obj(blsct_tx)

    return tx_outs

  def serialize(self) -> str:
    """Serialize the transaction to a hexadecimal string."""
    return blsct.to_hex(
      blsct.cast_to_uint8_t_ptr(self.value()),
      self.obj_size
    )

  @classmethod
  def deserialize(cls, hex: str) -> Self:
    """Deserialize a transaction from a hexadecimal string."""
    obj = blsct.hex_to_malloced_buf(hex)
    inst = cls(obj) 
    inst.obj_size = int(len(hex) / 2)
    return inst

  @override
  def value(self) -> Any:
    # self.obj is uint8_t*
    return blsct.cast_to_uint8_t_ptr(self.obj)

  @classmethod
  def default_obj(cls) -> Any:
    raise NotImplementedError("Cannot create a Tx without required parameters.")

