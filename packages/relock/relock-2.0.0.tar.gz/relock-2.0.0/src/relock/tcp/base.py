import pickle
import logging

from typing import Any
from time import sleep

class Base(object):

	def _get(self, _: bytes = bytes()):
		try:
			if self.connected:
				while slice := self.recv():
					_ += slice
					if len(slice) < self.length:
						break
		except ConnectionResetError:
			_ = bytes(1)
		else:
			if _ == b'PING':
				self.request.sendall(b'PONG')
			elif _ == b'PONG':
				pass
			elif _ == b'False':
				_ = False
			elif _ == b'True':
				_ = True
			elif _ == b'None':
				_ = None
			elif _ == b'SHUTDOWN':
				if not self.connected:
					self.shutdown(2)
			elif len(_) > 8:
				_ = self.xdh.decrypt(_)
		finally:
			sleep(0)
		return _

	def _put(self, _: bytes | bytes = bytes(), offset: int = 0, **kwargs) -> Any:
		if not len(kwargs) and _ == b'':
			_ = False #Can't send a null byte
		if not len(kwargs) and isinstance(_, (bool, type(None))):
			self.sendall(str(_).encode());  offset += self.length
		elif isinstance(_, bytes) and not len(kwargs) and len(_) < 8:
			self.sendall(bytes(_)); offset += self.length
		elif _ := self.xdh.encrypt(_ if _ else kwargs):
			while not offset >= len(_):
				if slice := _[offset:offset + self.length]:
					self.send(slice); offset += self.length
		return offset
