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

import datetime

class DateTimeTools():
	_CSHARP_EPOCH = datetime.datetime(1, 1, 1, 0, 0, 0)

	@classmethod
	def csharp_to_datetime(cls, csharp_ticks):
		seconds = csharp_ticks // 10000000
		residual = csharp_ticks % 10000000
		microseconds = residual // 10
		return cls._CSHARP_EPOCH + datetime.timedelta(0, seconds, microseconds)

	@classmethod
	def datetime_to_csharp(cls, datetime):
		seconds = (datetime - cls._CSHARP_EPOCH).total_seconds()
		return int(seconds) * 10000000

	@classmethod
	def csharp_now(cls):
		return cls.datetime_to_csharp(datetime.datetime.utcnow())
