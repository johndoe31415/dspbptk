#	dspbptk - Dyson Sphere Program Blueprint Toolkit
#	Copyright (C) 2021-2021 Johannes Bauer
#
#	This file is part of dspbptk.
#
#	dspbptk is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; this program is ONLY licensed under
#	version 3 of the License, later versions are explicitly excluded.
#
#	dspbptk is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#	Johannes Bauer <JohannesBauer@gmx.de>

import re
import math
import collections
import enum

class DysonSphereMD5():
	class Variant(enum.IntEnum):
		Original = 0
		MD5F = 1
		MD5FC = 2

	def _f(x, y, z):
		return (x & y) | (~x & z)

	def _g(x, y, z):
		return (x & z) | (y & ~z)

	def _h(x, y, z):
		return x ^ y ^ z

	def _i(x, y, z):
		return y ^ (x | ~z)

	@staticmethod
	def _rol(x, s):
		return ((x << s) | (x >> (32 - s))) & 0xffffffff

	_RoundOp = collections.namedtuple("RoundOp", [ "a", "b", "c", "d", "k", "s", "i", "T", "op" ])
	_ROUND_OPS = [
		_RoundOp(a = 0, b = 1, c = 2, d = 3, k =  0, s =  7, i =  1, T = 0xd76aa478, op = _f),
		_RoundOp(a = 3, b = 0, c = 1, d = 2, k =  1, s = 12, i =  2, T = 0xe8c7b756, op = _f),
		_RoundOp(a = 2, b = 3, c = 0, d = 1, k =  2, s = 17, i =  3, T = 0x242070db, op = _f),
		_RoundOp(a = 1, b = 2, c = 3, d = 0, k =  3, s = 22, i =  4, T = 0xc1bdceee, op = _f),
		_RoundOp(a = 0, b = 1, c = 2, d = 3, k =  4, s =  7, i =  5, T = 0xf57c0faf, op = _f),
		_RoundOp(a = 3, b = 0, c = 1, d = 2, k =  5, s = 12, i =  6, T = 0x4787c62a, op = _f),
		_RoundOp(a = 2, b = 3, c = 0, d = 1, k =  6, s = 17, i =  7, T = 0xa8304613, op = _f),
		_RoundOp(a = 1, b = 2, c = 3, d = 0, k =  7, s = 22, i =  8, T = 0xfd469501, op = _f),
		_RoundOp(a = 0, b = 1, c = 2, d = 3, k =  8, s =  7, i =  9, T = 0x698098d8, op = _f),
		_RoundOp(a = 3, b = 0, c = 1, d = 2, k =  9, s = 12, i = 10, T = 0x8b44f7af, op = _f),
		_RoundOp(a = 2, b = 3, c = 0, d = 1, k = 10, s = 17, i = 11, T = 0xffff5bb1, op = _f),
		_RoundOp(a = 1, b = 2, c = 3, d = 0, k = 11, s = 22, i = 12, T = 0x895cd7be, op = _f),
		_RoundOp(a = 0, b = 1, c = 2, d = 3, k = 12, s =  7, i = 13, T = 0x6b901122, op = _f),
		_RoundOp(a = 3, b = 0, c = 1, d = 2, k = 13, s = 12, i = 14, T = 0xfd987193, op = _f),
		_RoundOp(a = 2, b = 3, c = 0, d = 1, k = 14, s = 17, i = 15, T = 0xa679438e, op = _f),
		_RoundOp(a = 1, b = 2, c = 3, d = 0, k = 15, s = 22, i = 16, T = 0x49b40821, op = _f),
		_RoundOp(a = 0, b = 1, c = 2, d = 3, k =  1, s =  5, i = 17, T = 0xf61e2562, op = _g),
		_RoundOp(a = 3, b = 0, c = 1, d = 2, k =  6, s =  9, i = 18, T = 0xc040b340, op = _g),
		_RoundOp(a = 2, b = 3, c = 0, d = 1, k = 11, s = 14, i = 19, T = 0x265e5a51, op = _g),
		_RoundOp(a = 1, b = 2, c = 3, d = 0, k =  0, s = 20, i = 20, T = 0xe9b6c7aa, op = _g),
		_RoundOp(a = 0, b = 1, c = 2, d = 3, k =  5, s =  5, i = 21, T = 0xd62f105d, op = _g),
		_RoundOp(a = 3, b = 0, c = 1, d = 2, k = 10, s =  9, i = 22, T = 0x2441453, op = _g),
		_RoundOp(a = 2, b = 3, c = 0, d = 1, k = 15, s = 14, i = 23, T = 0xd8a1e681, op = _g),
		_RoundOp(a = 1, b = 2, c = 3, d = 0, k =  4, s = 20, i = 24, T = 0xe7d3fbc8, op = _g),
		_RoundOp(a = 0, b = 1, c = 2, d = 3, k =  9, s =  5, i = 25, T = 0x21e1cde6, op = _g),
		_RoundOp(a = 3, b = 0, c = 1, d = 2, k = 14, s =  9, i = 26, T = 0xc33707d6, op = _g),
		_RoundOp(a = 2, b = 3, c = 0, d = 1, k =  3, s = 14, i = 27, T = 0xf4d50d87, op = _g),
		_RoundOp(a = 1, b = 2, c = 3, d = 0, k =  8, s = 20, i = 28, T = 0x455a14ed, op = _g),
		_RoundOp(a = 0, b = 1, c = 2, d = 3, k = 13, s =  5, i = 29, T = 0xa9e3e905, op = _g),
		_RoundOp(a = 3, b = 0, c = 1, d = 2, k =  2, s =  9, i = 30, T = 0xfcefa3f8, op = _g),
		_RoundOp(a = 2, b = 3, c = 0, d = 1, k =  7, s = 14, i = 31, T = 0x676f02d9, op = _g),
		_RoundOp(a = 1, b = 2, c = 3, d = 0, k = 12, s = 20, i = 32, T = 0x8d2a4c8a, op = _g),
		_RoundOp(a = 0, b = 1, c = 2, d = 3, k =  5, s =  4, i = 33, T = 0xfffa3942, op = _h),
		_RoundOp(a = 3, b = 0, c = 1, d = 2, k =  8, s = 11, i = 34, T = 0x8771f681, op = _h),
		_RoundOp(a = 2, b = 3, c = 0, d = 1, k = 11, s = 16, i = 35, T = 0x6d9d6122, op = _h),
		_RoundOp(a = 1, b = 2, c = 3, d = 0, k = 14, s = 23, i = 36, T = 0xfde5380c, op = _h),
		_RoundOp(a = 0, b = 1, c = 2, d = 3, k =  1, s =  4, i = 37, T = 0xa4beea44, op = _h),
		_RoundOp(a = 3, b = 0, c = 1, d = 2, k =  4, s = 11, i = 38, T = 0x4bdecfa9, op = _h),
		_RoundOp(a = 2, b = 3, c = 0, d = 1, k =  7, s = 16, i = 39, T = 0xf6bb4b60, op = _h),
		_RoundOp(a = 1, b = 2, c = 3, d = 0, k = 10, s = 23, i = 40, T = 0xbebfbc70, op = _h),
		_RoundOp(a = 0, b = 1, c = 2, d = 3, k = 13, s =  4, i = 41, T = 0x289b7ec6, op = _h),
		_RoundOp(a = 3, b = 0, c = 1, d = 2, k =  0, s = 11, i = 42, T = 0xeaa127fa, op = _h),
		_RoundOp(a = 2, b = 3, c = 0, d = 1, k =  3, s = 16, i = 43, T = 0xd4ef3085, op = _h),
		_RoundOp(a = 1, b = 2, c = 3, d = 0, k =  6, s = 23, i = 44, T = 0x4881d05, op = _h),
		_RoundOp(a = 0, b = 1, c = 2, d = 3, k =  9, s =  4, i = 45, T = 0xd9d4d039, op = _h),
		_RoundOp(a = 3, b = 0, c = 1, d = 2, k = 12, s = 11, i = 46, T = 0xe6db99e5, op = _h),
		_RoundOp(a = 2, b = 3, c = 0, d = 1, k = 15, s = 16, i = 47, T = 0x1fa27cf8, op = _h),
		_RoundOp(a = 1, b = 2, c = 3, d = 0, k =  2, s = 23, i = 48, T = 0xc4ac5665, op = _h),
		_RoundOp(a = 0, b = 1, c = 2, d = 3, k =  0, s =  6, i = 49, T = 0xf4292244, op = _i),
		_RoundOp(a = 3, b = 0, c = 1, d = 2, k =  7, s = 10, i = 50, T = 0x432aff97, op = _i),
		_RoundOp(a = 2, b = 3, c = 0, d = 1, k = 14, s = 15, i = 51, T = 0xab9423a7, op = _i),
		_RoundOp(a = 1, b = 2, c = 3, d = 0, k =  5, s = 21, i = 52, T = 0xfc93a039, op = _i),
		_RoundOp(a = 0, b = 1, c = 2, d = 3, k = 12, s =  6, i = 53, T = 0x655b59c3, op = _i),
		_RoundOp(a = 3, b = 0, c = 1, d = 2, k =  3, s = 10, i = 54, T = 0x8f0ccc92, op = _i),
		_RoundOp(a = 2, b = 3, c = 0, d = 1, k = 10, s = 15, i = 55, T = 0xffeff47d, op = _i),
		_RoundOp(a = 1, b = 2, c = 3, d = 0, k =  1, s = 21, i = 56, T = 0x85845dd1, op = _i),
		_RoundOp(a = 0, b = 1, c = 2, d = 3, k =  8, s =  6, i = 57, T = 0x6fa87e4f, op = _i),
		_RoundOp(a = 3, b = 0, c = 1, d = 2, k = 15, s = 10, i = 58, T = 0xfe2ce6e0, op = _i),
		_RoundOp(a = 2, b = 3, c = 0, d = 1, k =  6, s = 15, i = 59, T = 0xa3014314, op = _i),
		_RoundOp(a = 1, b = 2, c = 3, d = 0, k = 13, s = 21, i = 60, T = 0x4e0811a1, op = _i),
		_RoundOp(a = 0, b = 1, c = 2, d = 3, k =  4, s =  6, i = 61, T = 0xf7537e82, op = _i),
		_RoundOp(a = 3, b = 0, c = 1, d = 2, k = 11, s = 10, i = 62, T = 0xbd3af235, op = _i),
		_RoundOp(a = 2, b = 3, c = 0, d = 1, k =  2, s = 15, i = 63, T = 0x2ad7d2bb, op = _i),
		_RoundOp(a = 1, b = 2, c = 3, d = 0, k =  9, s = 21, i = 64, T = 0xeb86d391, op = _i),
	]
	_ROUND_OP_PATCHES = {
		Variant.MD5F: {
			1: _RoundOp(a = 3, b = 0, c = 1, d = 2, k =  1, s = 12, i =  2, T = 0xe8d7b756, op = _f),
			6: _RoundOp(a = 2, b = 3, c = 0, d = 1, k =  6, s = 17, i =  7, T = 0xa8304623, op = _f),
			12: _RoundOp(a = 0, b = 1, c = 2, d = 3, k = 12, s =  7, i = 13, T = 0x6b9f1122, op = _f),
			15: _RoundOp(a = 1, b = 2, c = 3, d = 0, k = 15, s = 22, i = 16, T = 0x39b40821, op = _f),
			19: _RoundOp(a = 1, b = 2, c = 3, d = 0, k =  0, s = 20, i = 20, T = 0xc9b6c7aa, op = _g),
			21: _RoundOp(a = 3, b = 0, c = 1, d = 2, k = 10, s =  9, i = 22, T = 0x2443453, op = _g),
			24: _RoundOp(a = 0, b = 1, c = 2, d = 3, k =  9, s =  5, i = 25, T = 0x21f1cde6, op = _g),
			27: _RoundOp(a = 1, b = 2, c = 3, d = 0, k =  8, s = 20, i = 28, T = 0x475a14ed, op = _g),
		},
		Variant.MD5FC: {
			1: _RoundOp(a = 3, b = 0, c = 1, d = 2, k =  1, s = 12, i =  2, T = 0xe8d7b756, op = _f),
			3: _RoundOp(a = 1, b = 2, c = 3, d = 0, k =  3, s = 22, i =  4, T = 0xc1bdceef, op = _f),
			6: _RoundOp(a = 2, b = 3, c = 0, d = 1, k =  6, s = 17, i =  7, T = 0xa8304623, op = _f),
			12: _RoundOp(a = 0, b = 1, c = 2, d = 3, k = 12, s =  7, i = 13, T = 0x6b9f1122, op = _f),
			15: _RoundOp(a = 1, b = 2, c = 3, d = 0, k = 15, s = 22, i = 16, T = 0x39b40821, op = _f),
			19: _RoundOp(a = 1, b = 2, c = 3, d = 0, k =  0, s = 20, i = 20, T = 0xc9b6c7aa, op = _g),
			21: _RoundOp(a = 3, b = 0, c = 1, d = 2, k = 10, s =  9, i = 22, T = 0x2443453, op = _g),
			24: _RoundOp(a = 0, b = 1, c = 2, d = 3, k =  9, s =  5, i = 25, T = 0x23f1cde6, op = _g),
			27: _RoundOp(a = 1, b = 2, c = 3, d = 0, k =  8, s = 20, i = 28, T = 0x475a14ed, op = _g),
			34: _RoundOp(a = 2, b = 3, c = 0, d = 1, k = 11, s = 16, i = 35, T = 0x6d9d6121, op = _h),
		},
	}
	_INIT_VALUES = {
		Variant.Original: (
			int.from_bytes(bytes.fromhex("01 23 45 67"), byteorder = "little"),
			int.from_bytes(bytes.fromhex("89 ab cd ef"), byteorder = "little"),
			int.from_bytes(bytes.fromhex("fe dc ba 98"), byteorder = "little"),
			int.from_bytes(bytes.fromhex("76 54 32 10"), byteorder = "little"),
		),
		Variant.MD5F: (
			int.from_bytes(bytes.fromhex("01 23 45 67"), byteorder = "little"),
			int.from_bytes(bytes.fromhex("89 ab dc ef"), byteorder = "little"),
			int.from_bytes(bytes.fromhex("fe dc ba 98"), byteorder = "little"),
			int.from_bytes(bytes.fromhex("46 57 32 10"), byteorder = "little"),
		),
		Variant.MD5FC: (
			int.from_bytes(bytes.fromhex("01 23 45 67"), byteorder = "little"),
			int.from_bytes(bytes.fromhex("89 ab dc ef"), byteorder = "little"),
			int.from_bytes(bytes.fromhex("fe dc ba 98"), byteorder = "little"),
			int.from_bytes(bytes.fromhex("46 57 32 10"), byteorder = "little"),
		),
	}

	def __init__(self, variant = Variant.Original):
		(self._a, self._b, self._c, self._d) = self._INIT_VALUES[variant]
		self._buffer = bytearray()
		self._digest = None
		self._length = 0
		self._patches = self._ROUND_OP_PATCHES.get(variant, { })

	def _update_block(self, block):
		assert(len(block) == 64)
		state = [ self._a, self._b, self._c, self._d ]
		x = [ int.from_bytes(block[4 * i : 4 * (i + 1)], byteorder = "little") for i in range(16) ]

		for (i, round_op) in enumerate(self._ROUND_OPS):
			if i in self._patches:
				round_op = self._patches[i]
			a = state[round_op.a]
			b = state[round_op.b]
			c = state[round_op.c]
			d = state[round_op.d]
			state[round_op.a] = b + self._rol((a + round_op.op(b, c, d) + x[round_op.k] + round_op.T) & 0xffffffff, round_op.s)
		self._a = (self._a + state[0]) & 0xffffffff
		self._b = (self._b + state[1]) & 0xffffffff
		self._c = (self._c + state[2]) & 0xffffffff
		self._d = (self._d + state[3]) & 0xffffffff

	def _update(self, data, count_length = True):
		assert(self._digest is None)
		if count_length:
			self._length += len(data)
		self._buffer += data
		while len(self._buffer) >= 64:
			block = self._buffer[:64]
			self._buffer = self._buffer[64:]
			self._update_block(block)
		return self

	def update(self, data):
		return self._update(data)

	def _finalize(self):
		if self._digest is not None:
			return

		# Add padding
		padding_len = (64 - (self._length % 64) - 8) % 64
		if padding_len == 0:
			padding_len = 64
		self._update(bytes([ 0x80 ]), count_length = False)
		self._update(bytes([ 0 ] * (padding_len - 1)), count_length = False)

		# Add length
		length_bits = int.to_bytes(self._length * 8, length = 8, byteorder = "little")
		self._update(length_bits, count_length = False)

		# Concatenate digest
		self._digest = b"".join(int.to_bytes(x, length = 4, byteorder = "little") for x in [ self._a, self._b, self._c, self._d ])

	def digest(self):
		self._finalize()
		return self._digest

	def hexdigest(self):
		return self.digest().hex()

	@classmethod
	def _generate_block(cls, op, round_text):
		regex = re.compile(r"\[(?P<order>[A-D]{4})\s+(?P<k>\d+)\s+(?P<s>\d+)\s+(?P<i>\d+)\]")
		for match in regex.finditer(round_text):
			match = match.groupdict()
			a = "ABCD".index(match["order"][0])
			b = "ABCD".index(match["order"][1])
			c = "ABCD".index(match["order"][2])
			d = "ABCD".index(match["order"][3])
			k = int(match["k"])
			s = int(match["s"])
			i = int(match["i"])
			T = int(abs(math.sin(i)) * 0x100000000) & 0xffffffff
			print("\t\t_RoundOp(a = %d, b = %d, c = %d, d = %d, k = %2d, s = %2d, i = %2d, T = 0x%x, op = _%s)," % (a, b, c, d, k, s, i, T, op))

	@classmethod
	def generate(cls):
		cls._generate_block(op = "f", round_text = """
			[ABCD  0  7  1]  [DABC  1 12  2]  [CDAB  2 17  3]  [BCDA  3 22  4]
			[ABCD  4  7  5]  [DABC  5 12  6]  [CDAB  6 17  7]  [BCDA  7 22  8]
			[ABCD  8  7  9]  [DABC  9 12 10]  [CDAB 10 17 11]  [BCDA 11 22 12]
			[ABCD 12  7 13]  [DABC 13 12 14]  [CDAB 14 17 15]  [BCDA 15 22 16]
		""")
		cls._generate_block(op = "g", round_text = """
			[ABCD  1  5 17]  [DABC  6  9 18]  [CDAB 11 14 19]  [BCDA  0 20 20]
			[ABCD  5  5 21]  [DABC 10  9 22]  [CDAB 15 14 23]  [BCDA  4 20 24]
			[ABCD  9  5 25]  [DABC 14  9 26]  [CDAB  3 14 27]  [BCDA  8 20 28]
			[ABCD 13  5 29]  [DABC  2  9 30]  [CDAB  7 14 31]  [BCDA 12 20 32]
		""")
		cls._generate_block(op = "h", round_text = """
			[ABCD  5  4 33]  [DABC  8 11 34]  [CDAB 11 16 35]  [BCDA 14 23 36]
			[ABCD  1  4 37]  [DABC  4 11 38]  [CDAB  7 16 39]  [BCDA 10 23 40]
			[ABCD 13  4 41]  [DABC  0 11 42]  [CDAB  3 16 43]  [BCDA  6 23 44]
			[ABCD  9  4 45]  [DABC 12 11 46]  [CDAB 15 16 47]  [BCDA  2 23 48]
		""")
		cls._generate_block(op = "i", round_text = """
			[ABCD  0  6 49]  [DABC  7 10 50]  [CDAB 14 15 51]  [BCDA  5 21 52]
			[ABCD 12  6 53]  [DABC  3 10 54]  [CDAB 10 15 55]  [BCDA  1 21 56]
			[ABCD  8  6 57]  [DABC 15 10 58]  [CDAB  6 15 59]  [BCDA 13 21 60]
			[ABCD  4  6 61]  [DABC 11 10 62]  [CDAB  2 15 63]  [BCDA  9 21 64]
		""")

if __name__ == "__main__":
	import os
	import hashlib
	import sys

	if len(sys.argv) == 1:
		for i in range(200):
			data = os.urandom(i)
			right = hashlib.md5(data).hexdigest()
			mine = DysonSphereMD5().update(data).hexdigest()
			if right != mine:
				print(data.hex(), right, mine)
				raise Exception("Failed test cases.")

		assert(DysonSphereMD5(variant = DysonSphereMD5.Variant.MD5F).update(b"").hexdigest() == "84d1ce3bd68f49ab26eb0f96416617cf")
		assert(DysonSphereMD5(variant = DysonSphereMD5.Variant.MD5F).update(b"a").hexdigest() == "f10bddaecb62e5a92433757867ee06db")
		assert(DysonSphereMD5(variant = DysonSphereMD5.Variant.MD5F).update(b"abcd").hexdigest() == "fa27c78b6ec31559f0e760ce3f2b03f6")
		assert(DysonSphereMD5(variant = DysonSphereMD5.Variant.MD5F).update(b"Why are you doing this, Youthcat Studio?").hexdigest() == "13424e12890a3f50a1f8567c464fff8c")
		print("Passed testcases.")
	else:
		md = DysonSphereMD5(variant = DysonSphereMD5.Variant.MD5F)
		with open(sys.argv[1], "rb") as f:
			md.update(f.read())
		print(md.hexdigest())
