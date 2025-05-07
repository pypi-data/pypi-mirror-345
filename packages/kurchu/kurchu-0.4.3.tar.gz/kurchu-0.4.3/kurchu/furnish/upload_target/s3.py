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

from kurchu.furnish.upload_target.base import UploadTargetBase
import kurchu.util

log = logging.getLogger("kurchu")


class UploadTargetS3(UploadTargetBase):
	"""
	Implements S3 upload target
	"""

	def __init__(self, upload_config: dict, output_dir: Path) -> None:
		super().__init__(upload_config, output_dir)

	def upload(self) -> None:
		"""Upload to S3"""
		if self.generate_directory_index_page:
			log.info(f"Generating directory index pages for {self.compose_id}")
			self.generate_directory_indexes(self.output_dir)
		if self.target_subdir.startswith("/"):
			upload_subdir_path = self.target_subdir[1:]
		else:
			upload_subdir_path = self.target_subdir
		log.info(f"Uploading compose {self.compose_id} to s3://{self.name}/{upload_subdir_path}/")
		logfile = self.output_dir / f"./logs/furnish-{self.uploadtype}-{self.name}.log"
		logfile.parent.mkdir(parents=True, exist_ok=True)
		s3cmd_put_command = [
			"s3cmd",
			"put",
			"--recursive",
			"--acl-public",
			self.output_dir,
			f"s3://{self.name}/{upload_subdir_path}/",
		]
		if not self.public_read:
			s3cmd_put_command.remove("--acl-public")
		kurchu.util.run_command(s3cmd_put_command, logfile)
