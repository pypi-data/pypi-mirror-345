# Since this code makes use of Python's built-in large integer types, it is 
# NOT EXPECTED to run in constant time. While some effort is made to minimise 
# the time variations, the underlying functions are likely to have running 
# times that are highly value-dependent.

import logging
import hashlib
import os
import random
import sys
import pickle
import base64
import ctypes
import binascii

from typing import Any

from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.kdf.x963kdf import X963KDF
from cryptography.hazmat.primitives.kdf.hkdf import HKDFExpand
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes

from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.asymmetric import ed25519

from ..gcm import GCM

class Kyber(object):

	path = os.path.dirname(os.path.abspath(__file__))

	""" return None
	"""
	def __init__(self, *args,
					    iv: bytes = None,
					    power:int = 32):
		self.power    = power
		if os.popen("uname -m").read().strip() == 'arm64':
			self.file = '/mlkem768arm64.so'
		else:
			self.file = '/mlkem768x86_64.so'
		self.library  = ctypes.cdll.LoadLibrary(self.path + self.file)
		self.matrix   = args if len(args) else (os.urandom(power),)
		self.keygen()

	@property
	def matrix(self):
		return self.__matrix

	def keygen(self):
		keygen = self.library.keygen
		keygen.restype = ctypes.c_void_p
		bytes = ctypes.string_at(keygen())
		bytes = binascii.unhexlify(bytes.decode('utf-8'))
		self.public  = bytes[:1184]
		self.private = bytes[1184:]

	def encapsulate(self, pub:bytes):
		encapsulate = self.library.encapsulate
		encapsulate.argtypes = [ctypes.c_char_p]
		encapsulate.restype = ctypes.c_void_p
		out = encapsulate(binascii.hexlify(pub))
		bytes = binascii.unhexlify(ctypes.string_at(out))
		self.matrix = (bytes[:32],)
		return bytes[32:]

	def decapsulate(self, cipher:bytes):
		decapsulate = self.library.decapsulate
		decapsulate.argtypes = [ctypes.c_char_p,ctypes.c_char_p]
		decapsulate.restype = ctypes.c_void_p
		out = decapsulate(binascii.hexlify(self.private), 
						  binascii.hexlify(cipher))
		bytes = binascii.unhexlify(ctypes.string_at(out))
		self.matrix = (bytes,)

	@matrix.setter
	def matrix(self, args):
		self.__matrix = bytes()
		for _ in args:
			self.__matrix += _
		self.salt   = self.__matrix
		self.aead   = self.__matrix
		self.key    = self.__matrix
		self.engine = GCM(self.key)

	def __enter__(self):
		return self
 
	def __exit__(self, *args):
		del self.__iv

	""" return object self
	"""
	def __call__(self, iv:bytes = None):
		self.iv = iv or os.urandom(16)
		return self

	@property
	def salt(self):
		return bytes(self.__salt)

	@salt.setter
	def salt(self, value):
		if _ := sum(value):
			self.__salt = _.to_bytes((_.bit_length() + 7) // 8, 'little')

	@property
	def key(self):
		return bytes(self.__key)

	@key.setter
	def key(self, value):
		self.__key = hashlib.blake2b(value,
									 salt=self.salt,
									 digest_size=self.power).digest()

	@property
	def aead(self):
		""" returns 128 bits hash
		"""
		return bytes(self.__aead)

	@aead.setter
	def aead(self, value:bytes = bytes()):
		self.__aead = HKDFExpand(algorithm=hashes.SHA512(),
							     length=self.power,
							     info=self.salt).derive(value)

	@property
	def id(self):
		""" returns 128 bits hash
		"""
		return HKDFExpand(algorithm=hashes.SHA256(),
					      length=16,
					      info=self.salt).derive(self.key)

	@property
	def cipher(self) -> bytes:
		return self.__cipher

	@cipher.setter
	def cipher(self, value:bytes) -> None:
		self.__cipher = value

	@property
	def identity(self) -> bytes:
		return self.public

	@property
	def public(self) -> bytes:
		return self.__public

	@public.setter
	def public(self, value:bytes) -> None:
		self.__public = value

	@property
	def private(self) -> bytes:
		return self.__private

	@private.setter
	def private(self, value:bytes) -> None:
		self.__private = value

	def exchange(self, hex):
		if len(hex) == 1184:
			self.__cipher = self.encapsulate(hex)
		else:
			self.decapsulate(hex)
		return self

	""" return bytes, ciphertext
	"""
	def encrypt(self, data: Any) -> Any:
		with self.engine(self.aead) as engine:
			return engine.encrypt(data)
		return bytes()
	
	""" return bytes, plaintext
	"""
	def decrypt(self, data: Any) -> Any:
		try:
			with self.engine(self.aead) as engine:
				_ = engine.decrypt(data)
		except:
			return bytes()
		else:
			return _
			
	def __str__(self):
		return hashlib.blake2b(self.__matrix,
							   salt=bytes(),
							   digest_size=16).hexdigest()
