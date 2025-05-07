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

from kurchu.furnish.source import Source as FurnishSource
from kurchu.furnish.upload_target import UploadTarget as FurnishUploadTarget
import kurchu.util

log = logging.getLogger("kurchu")


def run(config: dict, output_dir: Path) -> None:
	"""Furnish the artifacts for consumption"""
	furnish_config = {}
	write_furnished_config = True
	# Store primary metadata
	log.info(f"Furnishing primary metadata for artifacts for {config["compose"]["compose_id"]}")
	furnish_config["compose"] = {}
	furnish_config["compose"]["compose_date"] = config["compose"]["compose_date"]
	furnish_config["compose"]["compose_id"] = config["compose"]["compose_id"]
	furnish_config["compose"]["release_name"] = config["compose"]["release_name"]
	furnish_config["compose"]["release_version"] = config["compose"]["release_version"]
	# Store gathered sources
	if "gather" in config["compose"] and "sources" in config["compose"]["gather"]:
		furnish_config["compose"]["gather"] = {}
		furnish_config["compose"]["gather"]["sources"] = []
		for source_config in config["compose"]["gather"]["sources"]:
			source_object = FurnishSource.new(source_config, output_dir)
			log.info(f"Furnishing source: {source_config['name']}")
			furnish_config["compose"]["gather"]["sources"].append(source_object.get_source_data())
	# Store compiled images
	if "compile" in config["compose"] and "images" in config["compose"]["compile"]:
		furnish_config["compose"]["compile"] = {"images": []}
		for furnished_image in config["compose"]["compile"]["images"]:
			if Path(output_dir / "compose" / furnished_image["target"]).exists():
				log.info(f"Furnishing image: {furnished_image['image_name']}")
				furnish_config["compose"]["compile"]["images"].append(furnished_image)
	# Store furnish settings
	furnish_config["compose"]["furnish"] = {}
	if "furnish" in config["compose"]:
		if config["compose"]["furnish"]["write_compose_info"] is not None:
			write_furnished_config = config["compose"]["furnish"]["write_compose_info"]
	furnish_config["compose"]["furnish"]["write_compose_info"] = write_furnished_config
	# Write the furnished config as json into the artifacts path
	if write_furnished_config:
		Path(output_dir / "compose").mkdir(parents=True, exist_ok=True)
		with open(file=output_dir / "compose" / "kurchu.artifacts.json", mode="wt") as artifacts_json:
			artifacts_json.write(kurchu.util.dict_to_prettyjson(furnish_config))
			log.info(f"Furnished artifacts information as {output_dir / "compose" / "kurchu.artifacts.json"}")
	if "upload_targets" in config["compose"]["furnish"]:
		for upload_target in config["compose"]["furnish"]["upload_targets"]:
			full_upload_target = upload_target | {"compose_id": config["compose"]["compose_id"]}
			upload_object = FurnishUploadTarget.new(full_upload_target, output_dir)
			upload_object.upload()
