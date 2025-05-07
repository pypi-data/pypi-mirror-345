# This file is part of kurchu.
#
# Licensed under the GNU General Public License Version 2
# Fedora-License-Identifier: GPLv2+
# SPDX-2.0-License-Identifier: GPL-2.0+
# SPDX-3.0-License-Identifier: GPL-2.0-or-later
#
# kurchu is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# kurchu is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with kurchu.  If not, see <https://www.gnu.org/licenses/>.


from pathlib import Path


class SourceBase:
	"""
	Base class for sources
	"""

	def __init__(self, source_config: dict, output_dir: Path) -> None:
		self.name = source_config["name"]
		self.url = source_config["url"]
		self.target_subdir = source_config["target"]
		self.sourcetype = source_config["type"]
		self.full_sync = source_config["sync"]
		self.id_file = None
		self.path_to_id = None
		self.source_id = None
		self.output_dir = output_dir

	def __enter__(self):
		return self

	def get_source_data(self) -> dict:
		"""Generic method to construct final source dictionary"""
		source_dict = {}
		source_dict["name"] = self.name
		if self.source_id is not None:
			furnish_url = ""
			if self.url.endswith("/"):
				furnish_url = self.url[:-1]
			furnish_url = furnish_url[: furnish_url.rfind("/")]
			furnish_url = f"{furnish_url}/{self.source_id}/"
			source_dict["url"] = furnish_url
		else:
			source_dict["url"] = self.url
		source_dict["target"] = self.target_subdir
		source_dict["type"] = self.sourcetype
		source_dict["sync"] = self.full_sync
		return source_dict
