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

import collections
from NamedStruct import NamedStruct
from Enums import DysonSphereItem, LogisticsStationDirection

class StationParameters():
	_Parameters = collections.namedtuple("Parameters", [ "work_energy", "drone_range", "vessel_range", "orbital_collector", "warp_distance", "equip_warper", "drone_count", "vessel_count" ])
	_STORAGE_OFFSET = 0
	_SLOTS_OFFSET = _STORAGE_OFFSET + 192
	_PARAMETERS_OFFSET = _SLOTS_OFFSET + 128

	def __init__(self, parameters, storage_len, slots_len):
		self._storage = self._parse_storage(parameters, storage_len)
		self._slots = self._parse_slots(parameters, slots_len)
		self._parameters = self._parse_parameters(parameters)

	@property
	def storage(self):
		return self._storage

	@property
	def slots(self):
		return self._slots

	@property
	def parameters(self):
		return self._parameters

	def _parse_storage(self, parameters, storage_len):
		storage = [ ]
		for offset in range(self._STORAGE_OFFSET, self._STORAGE_OFFSET + (6 * storage_len), 6):
			item_id = parameters[offset + 0]
			if item_id == 0:
				# Storage unused
				storage.append(None)
			else:
				storage.append({
					"item_id": parameters[offset + 0],
					"local_logic": parameters[offset + 1],
					"remote_logic": parameters[offset + 2],
					"max_count": parameters[offset + 3],
				})
		return storage

	def _parse_slots(self, parameters, slots_len):
		slots = [ ]
		for offset in range(self._SLOTS_OFFSET, self._SLOTS_OFFSET + (4 * slots_len), 4):
			storage_index = parameters[offset + 1]
			if storage_index == 0:
				# Slot unused
				slots.append(None)
			else:
				slots.append({
					"direction": LogisticsStationDirection(parameters[offset + 0]),
					"storage_index": parameters[offset + 1],
				})
		return slots

	def _parse_parameters(self, parameters):
		args = {
			"work_energy": parameters[self._PARAMETERS_OFFSET + 0],
			"drone_range": parameters[self._PARAMETERS_OFFSET + 1],
			"vessel_range": parameters[self._PARAMETERS_OFFSET + 2],
			"orbital_collector": (parameters[self._PARAMETERS_OFFSET + 3] == 1),
			"warp_distance": parameters[self._PARAMETERS_OFFSET + 4],
			"equip_warper":  (parameters[self._PARAMETERS_OFFSET + 5] == 1),
			"drone_count": parameters[self._PARAMETERS_OFFSET + 6],
			"vessel_count":  parameters[self._PARAMETERS_OFFSET + 7],
		}
		return self._Parameters(**args)

	def to_dict(self):
		return {
			"storage": self._storage,
			"slots": self._slots,
			"parameters": self._parameters._asdict(),
		}

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
	def item(self):
		try:
			return DysonSphereItem(self._fields.item_id)
		except ValueError:
			return None

	@property
	def data(self):
		return self._fields

	@property
	def raw_parameters(self):
		return self._parameters

	@property
	def parameters(self):
		if self.item == DysonSphereItem.PlanetaryLogisticsStation:
			return StationParameters(self._parameters, storage_len = 3, slots_len = 12)
		elif self.item == DysonSphereItem.InterstellarLogisticsStation:
			return StationParameters(self._parameters, storage_len = 5, slots_len = 12)
		return self._parameters

	@property
	def size(self):
		return self._BLUEPRINT_BUILDING.size + (len(self._parameters) * 4)

	def to_dict(self):
		result = self._fields._asdict()
		if self.item is not None:
			result["item_id"] = self.item.name
		result["parameters"] = self.parameters
		if not isinstance(result["parameters"], list):
			result["parameters"] = result["parameters"].to_dict()
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

	@classmethod
	def serialize(cls, data):
		bp = cls._HEADER.pack(data._header._asdict())
		for area in data._areas:
			bp += BlueprintArea._BLUEPRINT_AREA.pack(area.to_dict())
		bp += cls._BUILDING_HEADER.pack({"building_count": len(data._buildings)})
		for building in data._buildings:
			bp += BlueprintBuilding._BLUEPRINT_BUILDING.pack(building.data._asdict())
			bp += b''.join([i.to_bytes(4, byteorder = 'little') for i in building.raw_parameters])
		return bp
