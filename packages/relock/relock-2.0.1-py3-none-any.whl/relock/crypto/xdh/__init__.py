import logging
import hashlib
import os
import random
import sys
import pickle
import base64

from typing import Any

from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.kdf.x963kdf import X963KDF
from cryptography.hazmat.primitives.kdf.hkdf import HKDFExpand
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes

from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.backends.openssl.backend import backend

from ..gcm import GCM

class XDH(object):

	""" return None
	"""
	def __init__(self, *args,
					    iv: bytes = None,
					    power:int = 32):
		self.power    = power
		self.private  = args[0] if len(args) else self.make()
		self.matrix   = args if len(args) else (os.urandom(32),)
		self(iv)

	@property
	def iv(self):
		return self.__iv

	@iv.setter
	def iv(self, value):
		self.__iv = value or os.urandom(16)

	@property
	def matrix(self):
		return self.__matrix

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

	def __call__(self, iv:bytes = None):
		self.iv = iv or os.urandom(16)
		return self

	def make(self):
		return ed25519.Ed25519PrivateKey.generate().private_bytes(encoding=serialization.Encoding.Raw,
																  format=serialization.PrivateFormat.Raw,
																  encryption_algorithm=serialization.NoEncryption())

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
							     length=int(self.power/2),
							     info=self.salt).derive(value)

	@property
	def signer(self):
		if hasattr(self, '__signer'):
			return self.__signer

	@signer.setter
	def signer(self, value:bytes = bytes()):
		if isinstance(value, bytes):
			value = ed25519.Ed25519PublicKey.from_public_bytes(value)
		self.__signer = value

	@property
	def id(self):
		""" returns 128 bits string
		"""
		return base64.b64encode(HKDFExpand(algorithm=hashes.SHA256(),
									       length=16,
									       info=self.salt).derive(self.public)).decode()

	def sign(self, data:bytes) -> bytes:
		return self.ed25519.sign(data)

	def verify(self, data:bytes, signature:bytes) -> bool:
		try:
			self.signer.verify(signature, data)
		except:
			return False
		else:
			return True

	@property
	def public(self):
		return self.ed25519.public_key().public_bytes(
		    encoding=serialization.Encoding.Raw,
		    format=serialization.PublicFormat.Raw
		)

	@property
	def identity(self):
		return self.x25519.public_key().public_bytes(
		    encoding=serialization.Encoding.Raw,
		    format=serialization.PublicFormat.Raw
		)

	@property
	def x25519(self):
		if not backend.x25519_supported():
			raise UnsupportedAlgorithm(
				"X25519 is not supported by this version of OpenSSL.",
				_Reasons.UNSUPPORTED_EXCHANGE_ALGORITHM,
			)

		hasher = hashes.Hash(hashes.SHA512())
		hasher.update(self.private)
		h = bytearray(hasher.finalize())
		# curve25519 clamping
		h[0] &= 248
		h[31] &= 127
		h[31] |= 64

		return x25519.X25519PrivateKey.from_private_bytes(h[0:32])

	@property
	def ed25519(self):
		return ed25519.Ed25519PrivateKey.from_private_bytes(self.private)

	def exchange(self, hex):
		if public := x25519.X25519PublicKey.from_public_bytes(hex[0:32]):
			if shared := self.x25519.exchange(public):
				if _ := HKDF(algorithm=hashes.SHA512(),
						     length=32,
						     salt=None,
						     info=b'handshake data',
						).derive(shared):
					self.matrix = (_,)
					self.signer = public
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
			raise ValueError('Invalid decryption key.')
		else:
			return _
			
	def __str__(self):
		return 'XDH'