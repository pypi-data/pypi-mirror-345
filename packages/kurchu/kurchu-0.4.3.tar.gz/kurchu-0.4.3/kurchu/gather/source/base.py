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

import kurchu.util

log = logging.getLogger("kurchu")


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
		self.url_to_id = None
		self.source_id = None
		self.output_dir = output_dir

	def __enter__(self):
		return self

	def generate_gather_url(self) -> None:
		if self.source_id is not None:
			gather_url = ""
			if self.url.endswith("/"):
				gather_url = self.url[:-1]
			gather_url = gather_url[: gather_url.rfind("/")]
			gather_url = f"{gather_url}/{self.source_id}/"
			self.url = gather_url

	def download(self) -> None:
		"""Generic method to download sources"""
		self.generate_gather_url()
		if not self.full_sync and self.url_to_id is not None:
			download_targetpath = self.output_dir / "compose" / self.target_subdir
			log.info(f"Creating directory to store source metadata: {download_targetpath}")
			download_targetpath.mkdir(parents=True, exist_ok=True)
			log.info(f"Downloading source metadata from: {self.url_to_id}")
			urllib.request.urlretrieve(self.url_to_id, download_targetpath / self.id_file)
		else:
			self.lftp_mirror(self.name, self.sourcetype, self.url, self.output_dir, self.target_subdir)

	@staticmethod
	def lftp_mirror(name: str, sourcetype: str, url: str, dest: Path, target_subdir: Path) -> None:
		"""Mirror the specified url using lftp"""
		logfile = dest / f"./logs/gather-{sourcetype}-{name}.log"
		logfile.parent.mkdir(parents=True, exist_ok=True)
		mirrordir = dest / f"./compose/{target_subdir}"
		lftp_command = ["lftp", "-c", "mirror", "--verbose", "--continue", "--no-overwrite", "--delete", url, mirrordir]
		kurchu.util.run_command(lftp_command, logfile)
