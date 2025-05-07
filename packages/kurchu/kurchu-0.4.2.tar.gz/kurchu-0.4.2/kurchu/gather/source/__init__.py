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

from kurchu.util.exceptions import KurchuSourceSetupError

log = logging.getLogger("kurchu")


class Source(metaclass=ABCMeta):
	"""
	Factory for Source objects to derive the correct implementation
	"""

	@abstractmethod
	def __init__(self) -> None:
		return None

	@staticmethod
	def new(source_config: dict, output_dir: Path) -> object:
		sourcetype_map = {
			"yumrepo": "YumRepo",
			"kojidist": "KojiDist",
			"pungi": "Pungi",
			"bodhi": "Bodhi",
			"odcs": "ODCS",
		}
		try:
			source_class = [
				f"kurchu.gather.source.{source_config["type"]}",
				f"Source{sourcetype_map[source_config["type"]]}",
			]
			source_obj = importlib.import_module(source_class[0])
			module_name = source_class[1]
			return source_obj.__dict__[module_name](source_config, output_dir)
		except Exception as issue:
			raise KurchuSourceSetupError(f"Support for {source_config["type"]} not implemented: {issue}")
		log.info(f"Using source backend: {source_class[0]}")
