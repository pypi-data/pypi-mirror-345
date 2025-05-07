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

from kurchu.gather.source.base import SourceBase


class SourceYumRepo(SourceBase):
	"""
	Implements gathering the YUM repo source
	"""

	def __init__(self, source_config: dict, output_dir: Path) -> None:
		super().__init__(source_config, output_dir)

	def download(self) -> None:
		"""Download yum repo source"""
		self.lftp_mirror(self.name, self.sourcetype, self.url, self.output_dir, self.target_subdir)
