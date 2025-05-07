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

from urllib.parse import urlparse
from pathlib import Path
from typing import IO

import io
import json
import logging
import subprocess

from kurchu.util.exceptions import KurchuNonexistentPathError

log = logging.getLogger("kurchu")


def dict_to_prettyjson(data: dict) -> str:
	"""Print JSON of dictionary"""
	return json.dumps(data, sort_keys=True, indent=4, separators=(",", ": "))


def validate_url(url: str) -> bool:
	"""Validate URLs"""
	urlresult = urlparse(url)
	return bool(urlresult.scheme and urlresult.netloc)


def run_command(command: list, logfile_path: Path) -> subprocess.CompletedProcess | bool:
	log.info(f"Run command: {command}")
	if not logfile_path.parent.exists():
		raise KurchuNonexistentPathError(
			f"The directory '{logfile_path.parent}' for '{logfile_path.name}' does not exist."
		)
	with open(logfile_path, "w") as logfile:
		return subprocess.run(args=command, stdout=logfile, stderr=subprocess.STDOUT, text=True)


def pipe_to_log(stream: IO[str] | IO[bytes], log_prefix: str) -> None:
	"""Reads lines from a file-like object (bytes or text) and logs them."""
	if isinstance(stream, io.TextIOBase):
		for output_line in iter(stream.readline, ""):
			log.info(f"{log_prefix}: {output_line.rstrip()}")
	elif isinstance(stream, io.BufferedIOBase):
		for output_line in iter(stream.readline, b""):
			try:
				log.info(f"{log_prefix}: {output_line.decode("utf-8").rstrip()}")
			except UnicodeDecodeError:
				log.warning(f"{log_prefix}: Could not decode line: {output_line!r}")
	else:
		log.error(f"{log_prefix}: Unsupported stream type: {type(stream)}")
