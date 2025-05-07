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

from kurchu.util.exceptions import KurchuBuildSysSetupError

log = logging.getLogger("kurchu")


class BuildSys(metaclass=ABCMeta):
	"""
	Factory for BuildSys objects to derive the correct implementation
	"""

	@abstractmethod
	def __init__(self) -> None:
		return None

	@staticmethod
	def new(buildsys_name: str, buildsys_config: dict, output_dir: Path) -> object:
		buildsystype_map = {
			"koji": "Koji",
		}
		try:
			buildsys_class = [
				f"kurchu.compile.buildsys.{buildsys_config[buildsys_name]["type"]}",
				f"BuildSys{buildsystype_map[buildsys_config[buildsys_name]["type"]]}",
			]
			buildsys_obj = importlib.import_module(buildsys_class[0])
			module_name = buildsys_class[1]
			return buildsys_obj.__dict__[module_name](buildsys_name, buildsys_config, output_dir)
		except Exception as issue:
			raise KurchuBuildSysSetupError(
				f"Support for {buildsys_config[buildsys_name]["type"]} not implemented: {issue}"
			)
		log.info(f"Using buildsys backend: {buildsys_class[0]}")
