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
import os
import subprocess


class UploadTargetBase:
	"""
	Base class for upload targets
	"""

	def __init__(self, upload_config: dict, output_dir: Path) -> None:
		self.name = upload_config["name"]
		self.target_subdir = upload_config["target"]
		self.uploadtype = upload_config["type"]
		self.generate_directory_index_page = upload_config["generate_indexhtml"] or False
		self.public_read = upload_config["public"] or False
		self.compose_id = upload_config["compose_id"]
		self.output_dir = output_dir

	def __enter__(self):
		return self

	def upload(self) -> None:
		"""Base method for upload targets"""
		return None

	@staticmethod
	def generate_directory_indexes(basedir: Path) -> None:
		"""Generate directory index html pages using tree(1)"""
		tree_cmd = [
			"tree",
			"-h",
			"-a",
			"-H",
			".",
			"-L",
			"1",
			"-I",
			"index.html",
			"--noreport",
			"--charset",
			"utf-8",
			"-o",
			"index.html",
		]
		folders = [x[0] for x in os.walk(basedir)]

		for folder in folders:
			if os.path.exists(f"{folder}/index.html"):
				os.remove(f"{folder}/index.html")
			subprocess.run(tree_cmd, cwd=folder)
		return
