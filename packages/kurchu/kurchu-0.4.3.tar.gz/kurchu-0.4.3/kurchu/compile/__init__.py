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

from kurchu.compile.buildsys import BuildSys as CompileBuildSys

log = logging.getLogger("kurchu")


def prepare_imagebuild_cfg(
	imagebuild_config: dict, imagetool_config: dict, release_version: str, image_release: str
) -> dict:
	"""Prepare image build configuration dictionary"""
	imagebuild_config["release_version"] = release_version
	imagebuild_config["image_release"] = image_release
	for imagetool in imagetool_config.keys():
		if imagebuild_config["image_tool"] == imagetool:
			for imagetool_param in imagetool_config[imagetool].keys():
				if imagetool_param not in imagebuild_config:
					imagebuild_config[imagetool_param] = imagetool_config[imagetool][imagetool_param]
	return imagebuild_config


def imagebuild_task(buildsys_object: CompileBuildSys, imagebuild_config: dict) -> None:
	"""Run the image build tasks defined in the configuration"""
	log.info(f"Building image: {imagebuild_config["image_name"]}")
	buildsys_object.build_image(imagebuild_config)


def run(compile_config: dict, release_version: str, output_dir: Path) -> None:
	"""Run the compile step defined in the configuration"""
	buildsys_objects = {}
	for buildsys_cfg in compile_config["buildsys"].keys():
		buildsys_objects[buildsys_cfg] = CompileBuildSys.new(buildsys_cfg, compile_config["buildsys"], output_dir)
	gather_threads = []
	for imagecfg_dict in compile_config["images"]:
		imagebuild_config = prepare_imagebuild_cfg(
			imagecfg_dict, compile_config["image_tool"], release_version, compile_config["image_release"]
		)
		buildsys_object = buildsys_objects[imagebuild_config["buildsys"]]
		gt = threading.Thread(target=imagebuild_task, args=(buildsys_object, imagebuild_config))
		gt.start()
		gather_threads.append(gt)
	for gather_thread in gather_threads:
		gather_thread.join()
