import logging
import hashlib
import os
import random
import math
import sys
import pickle
import base64
import binascii
import xxhash

from typing import Any

from cryptography.exceptions import UnsupportedAlgorithm, _Reasons
from cryptography.hazmat.backends.openssl.backend import backend

from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.kdf.x963kdf import X963KDF
from cryptography.hazmat.primitives.kdf.hkdf import HKDFExpand
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes

from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.asymmetric import ed25519

from cryptography.hazmat.primitives.asymmetric.ed25519 import (Ed25519PrivateKey, 
															   Ed25519PublicKey)
from cryptography.hazmat.primitives.asymmetric.x25519 import (X25519PrivateKey, 
															  X25519PublicKey)
from cryptography.hazmat.primitives.serialization import (Encoding, 
														  NoEncryption, 
														  PrivateFormat, 
														  PublicFormat)

from fe25519 import fe25519
from ge25519 import ge25519, ge25519_p3

from ..gcm import GCM

logging = logging.Logger = logging.getLogger(__package__)

class Montgomery(object):

	def __init__(self, key):
		if isinstance(key, ed25519.Ed25519PrivateKey):
			key = key.private_bytes(encoding=serialization.Encoding.Raw,
									format=serialization.PrivateFormat.Raw,
									encryption_algorithm=serialization.NoEncryption())
		self.private = self.x25519_from_ed25519_private_bytes(key)
		self.public  = self.private.public_key()

	def x25519_from_ed25519_private_bytes(self, private_bytes):
		if not backend.x25519_supported():
			raise UnsupportedAlgorithm(
				"X25519 is not supported by this version of OpenSSL.",
				_Reasons.UNSUPPORTED_EXCHANGE_ALGORITHM,
			)

		hasher = hashes.Hash(hashes.SHA512())
		hasher.update(private_bytes)
		h = bytearray(hasher.finalize())
		# curve25519 clamping
		h[0] &= 248
		h[31] &= 127
		h[31] |= 64

		return x25519.X25519PrivateKey.from_private_bytes(h[0:32])

	@staticmethod
	def x25519_from_ed25519_public_bytes(public_bytes) -> X25519PublicKey:
		if not backend.x25519_supported():
			raise UnsupportedAlgorithm(
				"X25519 is not supported by this version of OpenSSL.",
				_Reasons.UNSUPPORTED_EXCHANGE_ALGORITHM,
			)

		# This is libsodium's crypto_sign_ed25519_pk_to_curve25519 translated into
		# the Pyton module ge25519.
		if ge25519.has_small_order(public_bytes) != 0:
			raise ValueError("Doesn't have small order")

		# frombytes in libsodium appears to be the same as
		# frombytes_negate_vartime; as ge25519 only implements the from_bytes
		# version, we have to do the root check manually.
		A = ge25519_p3.from_bytes(public_bytes)
		if A.root_check:
			raise ValueError("Root check failed")

		if not A.is_on_main_subgroup():
			raise ValueError("It's on the main subgroup")

		one_minus_y = fe25519.one() - A.Y
		x = A.Y + fe25519.one()
		x = x * one_minus_y.invert()

		return bytes(x.to_bytes())

	def secret(self, key):
		return self.private.exchange(x25519.X25519PublicKey.from_public_bytes(key))

	@property
	def public_bytes(self):
		return self.public.public_bytes(
			encoding=serialization.Encoding.Raw,
			format=serialization.PublicFormat.Raw
		)

	def __bytes__(self):
		return self.private.private_bytes(encoding=serialization.Encoding.Raw,
										  format=serialization.PrivateFormat.Raw,
										  encryption_algorithm=serialization.NoEncryption())

class Signer(object):

	def __init__(self, key):
		if not key:
			self.private = ed25519.Ed25519PrivateKey.generate()
		elif isinstance(key, bytes):
			self.private = ed25519.Ed25519PrivateKey.from_private_bytes(key)
		elif isinstance(key, ed25519.Ed25519PrivateKey):
			self.private = key
		else:
			raise ValueError('Signer key must be bytes or Ed225519.')
		self.public  = self.private.public_key()

	@property
	def key(self):
		return self.private

	def __bytes__(self):
		return self.public.public_bytes(encoding=serialization.Encoding.Raw,
										format=serialization.PublicFormat.Raw)

	def __abs__(self):
		return self.private.private_bytes(encoding=serialization.Encoding.Raw,
										  format=serialization.PrivateFormat.Raw,
										  encryption_algorithm=serialization.NoEncryption())

class KDM(object):

	""" return None
	"""
	def __init__(self, *args,
						power: int = 128):
		
		self.nonce    = os.urandom(16)
		self.power    = power

		self.private  = self.make_private_key()
		# self.public   = self.private.public_key()
		# self.x25519   = Montgomery(self.private)

		# self.signer = Signer(args[0] if len(args) else self.private)
		if len(args):
			setattr(self, '__signer', Signer(args[0]))

		self.client   = args[1] if len(args) else bytearray()
		self.session  = args[2] if len(args) else bytearray()
		self.secret   = args[3] if len(args) else bytearray(self.power)

	def __enter__(self):
		return self
 
	def __exit__(self, *args):
		del self.nonce

	def __call__(self, iv:bytes = None):
		self.iv = iv or os.urandom(16)
		return self

	def sign(self, data:bytes) -> bytes:
		return self.signer.key.sign(data)

	def verify(self, data:bytes, signature:bytes) -> bool:
		try:
			ed25519.Ed25519PublicKey.from_public_bytes(self.client).verify(signature, data)
		except:
			return False
		else:
			return True

	@property
	def x25519(self):
		if not hasattr(self, '__x25519'):
			self.__x25519 = Montgomery(self.private)
		return self.__x25519

	@property
	def signer(self):
		if not hasattr(self, '__signer'):
			setattr(self, '__signer', Signer(self.private))
		return getattr(self, '__signer')

	@property
	def public(self):
		if not hasattr(self, '__public'):
			self.__public = self.private.public_key()
		return self.__public
			
	@property
	def identity(self):
		return binascii.hexlify(bytes(self.signer))

	@staticmethod
	def make_private_key():
		return ed25519.Ed25519PrivateKey.generate()

	@classmethod
	def make_private_key_bytes(cls):
		return cls.make_private_key().private_bytes(encoding=serialization.Encoding.Raw,
												    format=serialization.PrivateFormat.Raw,
												    encryption_algorithm=serialization.NoEncryption())

	@property
	def public_bytes(self):
		return self.public.public_bytes(
			encoding=serialization.Encoding.Raw,
			format=serialization.PublicFormat.Raw
		)

	def exchange(self, key):
		self.client = key
		if bytes := self.x25519.secret(Montgomery.x25519_from_ed25519_public_bytes(key)):
			self.session = self.derive(bytes)
			if not len(self.secret):
				self.secret = self.expand(self.session, self.power)
		return self.public_bytes

	def rekeying(self, salt=bytes(), token=bytes()):
		if not isinstance(salt, bytes):
			raise ValueError('Salt must be an raw bytes.')
		if salt and len(salt) > 32:
			token = salt[int(len(salt) / 2):len(salt)]
		if not salt:
			salt = os.urandom(32)
		elif len(salt) > 32:
			salt = salt[0:int(len(salt) / 2)]
		self.secret = self.derive(self.secret, salt, len(self.secret))
		if token:
			return self.validate(token)
		return salt + self.token()

	def derive(self, key, salt=None, length=32, info=b'handshake data'):
		return HKDF(algorithm=hashes.SHA256(),
					length=length,
					salt=salt,
					info=info,
				).derive(key)

	def expand(self, key:bytes, max: int = 128, size:int = 32, slice:bytes = bytearray()) -> bytearray:
		slice.clear()
		while len(slice) < (max or sum(key)):
			key = hashlib.blake2b(key, salt=sum(key).to_bytes(16, 'little'),
									   digest_size=size).digest()
			slice += key
		return self.derive(slice, sum(key).to_bytes(16, 'little'), len(slice))

	def x(self, x:int = None, basepoint:int = 13) -> int:
		return self.pow_mod(basepoint, x, len(self.secret) - 1)

	def get(self, p:int, l:int, r:int = 32) -> int:
		g = pow(self.secret[len(self.secret) // 2], 2)
		x = self.x(p, g)
		if len(self.secret[x:x + r]) == r:
			return self.secret[x:x + r]
		else:
			return self.secret[x-r:x]
		return self.secret[x:x + r] if len(self.secret[x:x + r]) >= r else self.secret[x-r:x]

	def aead(self, random:bytes, salt:bytes = bytes(16), size:int = 16):
		bytearray = self.get(int.from_bytes(random[0:3], 'little'), 
						 	 int.from_bytes(random[3:4], 'little'))
		return hashlib.blake2b(bytearray,
							   salt=salt, 
							   digest_size=size).digest()

	def token(self, size:int = 32):
		if len(self.secret):
			random = os.urandom(int(size / 2))
			bytearray  = self.get(int.from_bytes(random[0:len(random)-1], 'little'), 
								  int.from_bytes(random[len(random)-1:len(random)], 'little'))
			bytearray  = Scrypt(length=len(random),
								salt=random,
							    n=2**8,
							    r=8,
							    p=1).derive(bytearray)
			return random + bytearray
		return bytes()

	def validate(self, token:bytes) -> bool:
		if bytearray := token:
			if salt := bytearray[0:int(len(token)/2)]:
				return bytearray[len(salt):] == Scrypt(salt=salt,
													   length=len(bytearray[len(salt):]),
													   n=2**8,
													   r=8,
													   p=1).derive(self.get(int.from_bytes(salt[0:len(salt)-1], 'little'), 
																  			int.from_bytes(salt[len(salt)-1:len(salt)], 'little')))


	def salt(self, random:bytes, salt:bytes = bytes(16), size:int = 16):
		bytearray = self.get(int.from_bytes(random[4:7], 'little'), 
							 int.from_bytes(random[7:8], 'little'))
		return Scrypt(salt=salt,
					  length=size,
					  n=2**16,
					  r=8,
					  p=1).derive(bytearray)

	def key(self, random:bytes, salt:bytes = bytes(), size:int = 16):
		bytearray = self.get(int.from_bytes(random[8:11], 'little'), 
						 	 int.from_bytes(random[11:12], 'little'))
		if salt:
			return hashlib.blake2b(bytearray,
								   salt=salt, 
								   digest_size=size).digest()
		return bytearray

	def crypto(self, key:bytes, salt:bytes):
		return self.derive(self.key(key), salt=salt, info=bytes())

	@property
	def id(self):
		return hashlib.blake2b(self.secret, salt=bytes(),
											digest_size=16).digest()

	def encrypt(self, data:bytes) -> bytes:
		if iv := os.urandom(12):
			if salt := self.salt(iv):
				if aead := self.aead(iv, salt):
					with GCM(self.crypto(iv, salt)) as gcm:
						return gcm(aead, iv).encrypt(data, True)
		return bytes()

	def decrypt(self, data:bytes) -> Any:
		if iv := data[0:12]:
			if salt := self.salt(iv):
				if aead := self.aead(iv, salt):
					with GCM(self.crypto(iv, salt)) as gcm:
						return gcm(aead, iv).decrypt(data[12:], True)
		return bytes()

	def pow_mod(self, a, e, m):
		if m == 1:
			return 0
		if e < 0:
			return self.pow_mod(self.mod_inv(a, m), -e, m)
		b = 1
		while e > 0:
			if e % 2 == 1:
				b = (b * a) % m
			a = (a * a) % m
			e >>= 1
		return b

	def mod_inv(self, a, m):
		m0 = m
		b, c = 1, 0
		while m != 0:
			q, r = divmod(a, m)
			a, b, c, m = m, c, b - q * c, r
		if a != 1:
			raise ValueError("Not invertible")
		if b < 0:
			b += m0
		return b


			
	def __str__(self):
		return 'KDM-X2N <%s>' % xxhash.xxh64(self.id).hexdigest()
