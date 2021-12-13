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

import os
from BaseAction import BaseAction
from Blueprint import Blueprint

class ActionEdit(BaseAction):
	def run(self):
		if (not self._args.force) and os.path.exists(self._args.outfile):
			print("Refusing to overwrite: %s" % (self._args.outfile))
			return 1

		bp = Blueprint.read_from_file(self._args.infile, validate_hash = not self._args.ignore_corrupt)
		if self._args.short_desc is not None:
			bp.short_desc = self._args.short_desc

		if self._args.search_item_id is not None and self._args.replacement_item_id is not None:
			bp.replace_item(self._args.search_item_id, self._args.replacement_item_id)

		bp.write_to_file(self._args.outfile)
