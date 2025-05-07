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


from configparser import ConfigParser
from pathlib import Path
import logging
import urllib.request

from kurchu.gather.source.base import SourceBase

log = logging.getLogger("kurchu")


class SourceODCS(SourceBase):
	"""
	Implements gathering the odcs compose source
	"""

	def __init__(self, source_config: dict, output_dir: Path) -> None:
		super().__init__(source_config, output_dir)
		self.id_file = ".composeinfo"
		self.url_to_id = f"{self.url}/compose/{self.id_file}"
		log.info(f"Identifying source ID for {self.name}")
		odcscomposeinfo_file = urllib.request.urlopen(self.url_to_id)
		odcscomposeinfo_cfg = ConfigParser()
		odcscomposeinfo_cfg.read_string(odcscomposeinfo_file.read().decode("utf-8"))
		odcscomposeinfo_file.close()
		self.source_id = odcscomposeinfo_cfg["compose"]["id"]
		log.info(f"Source ID for {self.name}: {self.source_id}")

	def download(self) -> None:
		"""Download odcs compose source"""
		self.generate_gather_url()
		if not self.full_sync:
			# This path seems weird, but it mimics what it would look like in a full download
			download_targetpath = self.output_dir / "compose" / self.target_subdir / "compose"
			log.info(f"Creating directory to store source metadata: {download_targetpath}")
			download_targetpath.mkdir(parents=True, exist_ok=True)
			log.info(f"Downloading source metadata from: {self.url_to_id}")
			urllib.request.urlretrieve(self.url_to_id, download_targetpath / self.id_file)
		else:
			self.lftp_mirror(self.name, self.sourcetype, self.url, self.output_dir, self.target_subdir)
