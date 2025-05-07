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
import io
import logging
import subprocess
import tempfile

import kurchu.util

log = logging.getLogger("kurchu")


class BuildSysBase:
	"""
	Base class for build systems
	"""

	def __init__(self, buildsys_name, buildsys_config: dict, output_dir: Path) -> None:
		self.name = buildsys_name
		self.buildsystype = buildsys_config[buildsys_name]["type"]
		self.extra_data = buildsys_config[buildsys_name]
		self.output_dir = output_dir

	def __enter__(self):
		return self

	def build_image(self, image_config: dict) -> None:
		"""Generic method to build an image"""
		pass

	@staticmethod
	def get_vcs_revision_from_ref(url: str, ref: str, vcstype: str) -> str | None:
		"""Derive the exact commit/revision from reference/branch/tag"""
		with tempfile.TemporaryDirectory() as vcstmpdir:
			vcstype_map = {"git": [f"git clone {url} {vcstmpdir}", f"git checkout {ref}", "git rev-parse HEAD"]}
			if vcstype not in vcstype_map.keys():
				return None
			log.info(f"Determining revision for {vcstype} repository {url} at reference {ref}")
			for vcs_command in vcstype_map[vcstype][:-1]:
				vcs_process = subprocess.Popen(
					vcs_command.split(), cwd=vcstmpdir, stdout=subprocess.PIPE, stderr=subprocess.PIPE
				)
				stdout_reader = io.TextIOWrapper(vcs_process.stdout, encoding="utf-8", errors="replace")
				stderr_reader = io.TextIOWrapper(vcs_process.stderr, encoding="utf-8", errors="replace")
				while True:
					stdout_line = stdout_reader.readline()
					if stdout_line:
						kurchu.util.pipe_to_log(io.StringIO(stdout_line), vcstype + "-stdout")
					stderr_line = stderr_reader.readline()
					if stderr_line:
						kurchu.util.pipe_to_log(io.StringIO(stderr_line), vcstype + "-stderr")
					if not stdout_line and not stderr_line:
						break
				vcs_proc_exitcode = vcs_process.wait()
				stdout_reader.close()
				stderr_reader.close()
				vcs_process.stdout.close()
				vcs_process.stderr.close()
				if vcs_proc_exitcode != 0:
					log.error(f"{vcstype} command '{vcs_command}' failed with exit code: {vcs_proc_exitcode}")
					return None
			vcs_revproc = subprocess.run(
				vcstype_map[vcstype][-1].split(), cwd=vcstmpdir, text=True, capture_output=True
			)
			vcsrev = vcs_revproc.stdout
			log.info(f"Revision for {vcstype} repository {url} at reference {ref}: {vcsrev}")
			return vcsrev

	@staticmethod
	def lftp_mirror(name: str, buildsysname: str, buildsystype: str, url: str, dest: Path, target_subdir: Path) -> None:
		"""Mirror the specified url using lftp"""
		logfile = dest / f"./logs/compile-{buildsysname}-{buildsystype}-{name}.log"
		logfile.parent.mkdir(parents=True, exist_ok=True)
		mirrordir = dest / f"./compose/{target_subdir}"
		lftp_command = ["lftp", "-c", "mirror", "--verbose", "--continue", "--no-overwrite", "--delete", url, mirrordir]
		kurchu.util.run_command(lftp_command, logfile)
