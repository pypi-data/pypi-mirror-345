import blsct
from abc import ABC, abstractmethod
from typing import Any, Self

class ManagedObj(ABC):
  def __init__(self, obj=None):
    self.obj = self.default_obj() if obj is None else obj
    self._managed = False

  @abstractmethod
  def value(self):
    pass

  @classmethod
  def default_obj(cls) -> Any:
    name = cls.__name__
    raise NotImplementedError(f"{name}.default_obj()")

  def move(self) -> Any:
    if self.obj is None:
      raise ValueError("Object is None")
    obj = self.obj
    self.obj = None
    return obj

  def __del__(self):
    if self.obj is not None:
      blsct.free_obj(self.obj)

  def __enter__(self):
    self._managed = True
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    if self.obj is not None and self._managed is True:
      blsct.free_obj(self.obj)
      self.obj = None
    return False

  def __str__(self):
    name = self.__class__.__name__
    if hasattr(self, "to_hex"):
      return f"{name}({self.to_hex()})"
    else:
      return f"{name}({self.obj})"

  @classmethod
  def from_obj(cls, obj):
    inst = cls.__new__(cls)
    inst.obj = obj
    inst._managed = False
    return inst

