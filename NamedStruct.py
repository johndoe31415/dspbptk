#!/usr/bin/python3
#
#	NamedStruct - Python structure that has named member entries
#	Copyright (C) 2017-2021 Johannes Bauer
#
#	This file is part of pycommon.
#
#	pycommon is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; this program is ONLY licensed under
#	version 3 of the License, later versions are explicitly excluded.
#
#	pycommon is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with pycommon; if not, write to the Free Software
#	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#	Johannes Bauer <JohannesBauer@gmx.de>
#
#	File UUID 34de558f-8b40-4899-a9d9-66e46d7d07a4

import collections
import struct

class NamedStruct():
	def __init__(self, fields, struct_extra = "<"):
		struct_format = struct_extra + ("".join(fieldtype for (fieldtype, fieldname) in fields))
		self._struct = struct.Struct(struct_format)
		self._collection = collections.namedtuple("Fields", [ fieldname for (fieldtype, fieldname) in fields ])

	@property
	def size(self):
		return self._struct.size

	def pack(self, data):
		fields = self._collection(**data)
		return self._struct.pack(*fields)

	def unpack(self, data):
		values = self._struct.unpack(data)
		fields = self._collection(*values)
		return fields

	def unpack_head(self, data, offset = 0):
		return self.unpack(data[offset : offset + self._struct.size])

	def unpack_from_file(self, f, at_offset = None):
		if at_offset is not None:
			f.seek(at_offset)
		data = f.read(self._struct.size)
		return self.unpack(data)
