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


from abc import ABCMeta, abstractmethod
from pathlib import Path
import importlib
import logging

from kurchu.util.exceptions import KurchuUploadTargetSetupError

log = logging.getLogger("kurchu")


class UploadTarget(metaclass=ABCMeta):
	"""
	Factory for UploadTarget objects to derive the correct implementation
	"""

	@abstractmethod
	def __init__(self) -> None:
		return None

	@staticmethod
	def new(upload_config: dict, output_dir: Path) -> object:
		uploadtype_map = {
			"s3": "S3",
		}
		try:
			uploadtarget_class = [
				f"kurchu.furnish.upload_target.{upload_config["type"]}",
				f"UploadTarget{uploadtype_map[upload_config["type"]]}",
			]
			uploadtarget_obj = importlib.import_module(uploadtarget_class[0])
			module_name = uploadtarget_class[1]
			return uploadtarget_obj.__dict__[module_name](upload_config, output_dir)
		except Exception as issue:
			raise KurchuUploadTargetSetupError(f"Support for {upload_config["type"]} not implemented: {issue}")
		log.info(f"Using upload target backend: {uploadtarget_class[0]}")
