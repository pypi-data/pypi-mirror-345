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
import json
import logging
import urllib.request


from kurchu.gather.source.base import SourceBase

log = logging.getLogger("kurchu")


class SourceKojiDist(SourceBase):
	"""
	Implements gathering the koji dist-repos source
	"""

	def __init__(self, source_config: dict, output_dir: Path) -> None:
		super().__init__(source_config, output_dir)
		self.id_file = "repo.json"
		self.url_to_id = f"{self.url}/{self.id_file}"
		log.info(f"Identifying source ID for {self.name}")
		kojidistrepo_file = urllib.request.urlopen(self.url_to_id)
		kojidistrepo_dict = json.load(kojidistrepo_file)
		kojidistrepo_file.close()
		self.source_id = kojidistrepo_dict["id"]
		log.info(f"Source ID for {self.name}: {self.source_id}")
