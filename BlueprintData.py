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

from NamedStruct import NamedStruct
from Enums import DysonSphereItem

class BlueprintArea():
	_BLUEPRINT_AREA = NamedStruct((
		("b", "index"),
		("b", "parent_index"),
		("H", "tropic_anchor"),
		("H", "area_segments"),
		("H", "anchor_local_offset_x"),
		("H", "anchor_local_offset_y"),
		("H", "width"),
		("H", "height"),
	))

	def __init__(self, fields):
		self._fields = fields

	@property
	def size(self):
		return self._BLUEPRINT_AREA.size

	def to_dict(self):
		return self._fields._asdict()

	@classmethod
	def deserialize(cls, data, offset):
		fields = cls._BLUEPRINT_AREA.unpack_head(data, offset)
		return cls(fields)

class BlueprintBuilding():
	_BLUEPRINT_BUILDING = NamedStruct((
		("L", "index"),
		("b", "area_index"),
		("f", "local_offset_x"),
		("f", "local_offset_y"),
		("f", "local_offset_z"),
		("f", "local_offset_x2"),
		("f", "local_offset_y2"),
		("f", "local_offset_z2"),
		("f", "yaw"),
		("f", "yaw2"),
		("H", "item_id"),
		("H", "model_index"),
		("L", "output_object_index"),
		("L", "input_object_index"),
		("b", "output_to_slot"),
		("b", "input_from_slot"),
		("b", "output_from_slot"),
		("b", "input_to_slot"),
		("b", "output_offset"),
		("b", "input_offset"),
		("H", "recipe_id"),
		("H", "filter_id"),
		("H", "parameter_count"),
	))

	def __init__(self, fields, parameters):
		self._fields = fields
		self._parameters = parameters

	@property
	def data(self):
		return self._fields

	@property
	def parameters(self):
		return self._parameters

	@property
	def size(self):
		return self._BLUEPRINT_BUILDING.size + (len(self._parameters) * 4)

	def to_dict(self):
		result = self._fields._asdict()
		try:
			item = DysonSphereItem(result["item_id"])
			result["item_id"] = item.name
		except ValueError:
			pass
		result["parameters"] = self._parameters
		return result

	@classmethod
	def deserialize(cls, data, offset):
		fields = cls._BLUEPRINT_BUILDING.unpack_head(data, offset)
		offset += cls._BLUEPRINT_BUILDING.size

		parameters = [ int.from_bytes(data[offset + 4 * i : offset + (4 * (i + 1)) ], byteorder = "little") for i in range(fields.parameter_count) ]
		return cls(fields, parameters)

class BlueprintData():
	_HEADER = NamedStruct((
		("L", "version"),
		("L", "cursor_offset_x"),
		("L", "cursor_offset_y"),
		("L", "cursor_target_area"),
		("L", "dragbox_size_x"),
		("L", "dragbox_size_y"),
		("L", "primary_area_index"),
		("B", "area_count"),
	))
	_BUILDING_HEADER = NamedStruct((
		("L", "building_count"),
	))

	def __init__(self, header, areas, buildings):
		self._header = header
		self._areas = areas
		self._buildings = buildings

	@property
	def buildings(self):
		return self._buildings

	def to_dict(self):
		result = self._header._asdict()
		result["areas"] = [ area.to_dict() for area in self._areas ]
		result["buildings"] = [ building.to_dict() for building in self._buildings ]
		return result

	@classmethod
	def deserialize(cls, data):
		header = cls._HEADER.unpack_head(data)

		areas = [ ]
		offset = cls._HEADER.size
		for area_id in range(header.area_count):
			area = BlueprintArea.deserialize(data, offset)
			offset += area.size
			areas.append(area)

		buildings = [ ]
		building_header = cls._BUILDING_HEADER.unpack_head(data, offset)
		offset += cls._BUILDING_HEADER.size
		for building_id in range(building_header.building_count):
			building = BlueprintBuilding.deserialize(data, offset)
			offset += building.size
			buildings.append(building)

		return cls(header, areas, buildings)
