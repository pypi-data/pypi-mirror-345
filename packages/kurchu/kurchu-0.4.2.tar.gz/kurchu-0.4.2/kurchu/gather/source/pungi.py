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
import logging
import urllib.request

from kurchu.gather.source.base import SourceBase

log = logging.getLogger("kurchu")


class SourcePungi(SourceBase):
	"""
	Implements gathering the pungi compose source
	"""

	def __init__(self, source_config: dict, output_dir: Path) -> None:
		super().__init__(source_config, output_dir)
		self.id_file = "COMPOSE_ID"
		self.url_to_id = f"{self.url}/{self.id_file}"
		log.info(f"Identifying source ID for {self.name}")
		pungicomposeid_file = urllib.request.urlopen(self.url_to_id)
		self.source_id = pungicomposeid_file.read().decode("utf-8")
		pungicomposeid_file.close()
		log.info(f"Source ID for {self.name}: {self.source_id}")
