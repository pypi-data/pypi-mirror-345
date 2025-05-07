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
import threading

from kurchu.gather.source import Source as GatherSource

log = logging.getLogger("kurchu")


def gather_task(source_config: dict, output_dir: Path) -> None:
	"""Gather the source defined in the configuration"""
	source_object = GatherSource.new(source_config, output_dir)
	log.info(f"Gathering source: {source_config['name']}")
	source_object.download()


def run(sources_config: dict, output_dir: Path) -> None:
	"""Gather the sources defined in the configuration"""
	gather_threads = []
	for source_config in sources_config:
		gt = threading.Thread(target=gather_task, args=(source_config, output_dir))
		gt.start()
		gather_threads.append(gt)
	for gather_thread in gather_threads:
		gather_thread.join()
