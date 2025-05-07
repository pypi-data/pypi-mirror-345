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


from argparse import ArgumentParser
from pathlib import Path
import logging

import kurchu.compile
import kurchu.config
import kurchu.furnish
import kurchu.gather
import kurchu.util

log = logging.getLogger("kurchu")


def cli_main():
	"""Main command-line interface"""
	parser = ArgumentParser(description="gather Fedora/CentOS resources to create artifact collections")
	parser.add_argument("config", type=Path, default="kurchu.toml", help="Path to configuration file written in TOML")
	parser.add_argument("--dest", "-d", type=Path, help="Path to store artifact collection")
	parser.add_argument("--logfile", "-l", type=Path, default=None, help="Override path to log file")
	args = parser.parse_args()

	# Read config from TOML to dictionary
	kurchu_config_dict = kurchu.config.process_config(kurchu.config.read_config(args.config))
	# Set up destination
	base_destdir = args.dest or Path(kurchu_config_dict["compose"].get("destdir", "./artifacts"))
	artifacts_dest = base_destdir / kurchu_config_dict["compose"]["compose_id"]
	# Set up logfile path
	if not args.logfile:
		logfile = artifacts_dest / "logs" / "kurchu.log"
	else:
		logfile = args.logfile
	logfile.parent.mkdir(parents=True, exist_ok=True)
	logging.basicConfig(filename=logfile, encoding="utf-8", level=logging.DEBUG)
	# Print config to the screen
	print(kurchu.util.dict_to_prettyjson(kurchu_config_dict))
	# Gather sources
	if "gather" in kurchu_config_dict["compose"] and "sources" in kurchu_config_dict["compose"]["gather"]:
		print("Gathering sources...")
		kurchu_sources_list = kurchu_config_dict["compose"]["gather"]["sources"]
		kurchu.gather.run(kurchu_sources_list, artifacts_dest)
		print("Completed gathering sources!")
	# Compile images
	if "compile" in kurchu_config_dict["compose"]:
		print("Compiling images...")
		kurchu_compile_dict = kurchu_config_dict["compose"]["compile"]
		kurchu_config_releasever = kurchu_config_dict["compose"]["release_version"]
		kurchu.compile.run(kurchu_compile_dict, kurchu_config_releasever, artifacts_dest)
		print("Completed compiling images!")
	# Furnish artifacts
	kurchu.furnish.run(kurchu_config_dict, artifacts_dest)
