#	dspbptk - Dyson Sphere Program Blueprint Toolkit
#	Copyright (C) 2021-2022 Johannes Bauer
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

import datetime
import gzip
import base64
import urllib.parse
from MD5 import DysonSphereMD5
from Tools import DateTimeTools
from BlueprintData import BlueprintData

class Blueprint():
	def __init__(self, game_version, data, layout = 10, icon0 = 0, icon1 = 0, icon2 = 0, icon3 = 0, icon4 = 0, timestamp = None, short_desc = "Short description", long_desc = "Long description"):
		if timestamp is None:
			timestamp = DateTimeTools.csharp_now()
		self._layout = layout
		self._icon0 = icon0
		self._icon1 = icon1
		self._icon2 = icon2
		self._icon3 = icon3
		self._icon4 = icon4
		self._timestamp = timestamp
		self._game_version = game_version
		self._short_desc = short_desc
		self._long_desc = long_desc
		self._data = data

	@property
	def timestamp(self):
		return self._timestamp

	@timestamp.setter
	def timestamp(self, value):
		assert(isinstance(value, datetime.datetime))
		self._timestamp = value

	@property
	def game_version(self):
		return self._game_version

	@property
	def short_desc(self):
		return self._short_desc

	@short_desc.setter
	def short_desc(self, value):
		assert(isinstance(value, str))
		self._short_desc = value

	@property
	def long_desc(self):
		return self._long_desc

	@long_desc.setter
	def long_desc(self, value):
		assert(isinstance(value, str))
		self._long_desc = value

	@property
	def decoded_data(self):
		return BlueprintData.deserialize(self._data)

	@classmethod
	def from_blueprint_string(cls, bp_string, validate_hash = True):
		if validate_hash:
			index = bp_string.rindex("\"")
			hashed_data = bp_string[:index]
			ref_value = bp_string[index + 1 : ].lower().strip()
			hash_value = DysonSphereMD5(DysonSphereMD5.Variant.MD5F).update(hashed_data.encode("utf-8")).hexdigest()
			if ref_value != hash_value:
				raise InvalidHashValueException("Blueprint string has invalid has value.")

		assert(bp_string.startswith("BLUEPRINT:"))
		components = bp_string[10:].split(",")

		assert(len(components) == 12)
		(fixed0_1, layout, icon0, icon1, icon2, icon3, icon4, fixed0_2, timestamp, game_version, short_desc, b64data_hash) = components

		(fixed0_1, layout, icon0, icon1, icon2, icon3, icon4, fixed0_2, timestamp) = (int(fixed0_1), int(layout), int(icon0), int(icon1), int(icon2), int(icon3), int(icon4), int(fixed0_2), int(timestamp))
		assert(fixed0_1 == 0)
		assert(fixed0_2 == 0)
		timestamp = DateTimeTools.csharp_to_datetime(timestamp)
		short_desc = urllib.parse.unquote(short_desc)

		b64data_hash_split = b64data_hash.split("\"")
		assert(len(b64data_hash_split) == 3)

		(long_desc, b64data, hash_value) = b64data_hash_split
		long_desc = urllib.parse.unquote(long_desc)
		compressed_data = base64.b64decode(b64data)
		data = gzip.decompress(compressed_data)
		return cls(layout = layout, icon0 = icon0, icon1 = icon1, icon2 = icon2, icon3 = icon3, icon4 = icon4, timestamp = timestamp, game_version = game_version, short_desc = short_desc, long_desc = long_desc, data = data)

	def serialize(self):
		compressed_data = gzip.compress(self._data)
		b64_data = base64.b64encode(compressed_data).decode("ascii")

		components = [ ]
		components.append("0")
		components.append(str(self._layout))
		components.append(str(self._icon0))
		components.append(str(self._icon1))
		components.append(str(self._icon2))
		components.append(str(self._icon3))
		components.append(str(self._icon4))
		components.append("0")
		components.append(str(DateTimeTools.datetime_to_csharp(self._timestamp)))
		components.append(self._game_version)
		components.append(urllib.parse.quote(self._short_desc))
		header = "BLUEPRINT:" + ",".join(components)
		hashed_data = header + ",\"" + b64_data
		hash_value = DysonSphereMD5(DysonSphereMD5.Variant.MD5F).update(hashed_data.encode("utf-8")).hexdigest()
		return hashed_data + "\"" + hash_value.upper()

	def to_dict(self):
		return {
			"icon": {
				"layout": self._layout,
				"images": [ self._icon0, self._icon1, self._icon2, self._icon3, self._icon4 ],
			},
			"timestamp": self._timestamp.strftime("%Y-%m-%d %H:%M:%S"),
			"game_version": self._game_version,
			"short_desc": self._short_desc,
			"data": self.decoded_data.to_dict(),
		}

	@classmethod
	def read_from_file(cls, filename, validate_hash = True):
		with open(filename) as f:
			return cls.from_blueprint_string(f.read(), validate_hash = validate_hash)

	def write_to_file(self, filename):
		with open(filename, "w") as f:
			f.write(self.serialize())
