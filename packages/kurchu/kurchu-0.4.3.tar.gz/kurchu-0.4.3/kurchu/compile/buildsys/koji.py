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


import logging

import kurchu.util

from kurchu.compile.buildsys.base import BuildSysBase

log = logging.getLogger("kurchu")


class BuildSysKoji(BuildSysBase):
	"""
	Implements compiling with the Koji build system
	"""

	def build_image(self, image_config: dict) -> None:
		"""Method to build an image using Koji"""
		imagetoolcmd_map = {
			"kiwi": ["kiwi-build", "kiwi_description"],
		}
		koji_basecmd = f"koji --profile={self.extra_data["koji_profile"]}"
		koji_buildbasecmd = (
			f"{koji_basecmd} {imagetoolcmd_map[image_config["image_tool"]][0]} {self.extra_data["koji_build_tag"]}"
		)
		vcs_url = image_config[imagetoolcmd_map[image_config["image_tool"]][1]]["url"]
		vcs_type = image_config[imagetoolcmd_map[image_config["image_tool"]][1]]["vcs"]
		vcs_ref = image_config[imagetoolcmd_map[image_config["image_tool"]][1]]["ref"]
		vcs_rev = self.get_vcs_revision_from_ref(vcs_url, vcs_ref, vcs_type)
		koji_vcsurl = f"{vcs_type}+{vcs_url}#{vcs_rev}"
		koji_buildcmd = f"{koji_buildbasecmd} {koji_vcsurl}"
		if image_config["image_tool"] == "kiwi":
			koji_kiwibuild_params = f"{image_config["kiwi_description"]["path"]} --type={image_config["image_type"]} --kiwi-profile={image_config["variant"]} --release={image_config["image_release"]}"
			if "kiwi_result_bundle_name_format" not in image_config:
				koji_kiwibuild_params += " --result-bundle-name-format=%N-%v-%I.%A"
			else:
				koji_kiwibuild_params += (
					f" --result-bundle-name-format={image_config["kiwi_result_bundle_name_format"]}"
				)
			if "arch" in image_config:
				for buildarch in image_config["arch"]:
					koji_kiwibuild_params += f" --arch={buildarch}"
			if "volid_prefix" in image_config and image_config["image_type"] == "iso":
				koji_kiwibuild_params += f" --type-attr=volid={image_config["volid_prefix"]}-{image_config["release_version"]}-{image_config["image_release"]}"
			if "appid_prefix" in image_config and image_config["image_type"] == "iso":
				koji_kiwibuild_params += f" --type-attr=application_id={image_config["appid_prefix"]}-{image_config["release_version"]}-{image_config["image_release"]}"
			koji_buildcmd = f"{koji_buildcmd} {koji_kiwibuild_params}"
		log.info(
			f"Building {image_config["image_name"]}-{image_config["release_version"]}-{image_config["image_release"]} on {image_config["buildsys"]} Koji instance using {image_config["image_tool"]}"
		)
		logfile = (
			self.output_dir
			/ f"./logs/compile-{image_config["buildsys"]}-{self.buildsystype}-{image_config["image_tool"]}-{image_config["image_name"]}.log"
		)
		logfile.parent.mkdir(parents=True, exist_ok=True)
		buildrun = kurchu.util.run_command(koji_buildcmd.split(), logfile)
		if buildrun.returncode == 0:
			koji_tagbuild_basecmd = f"{koji_basecmd} tag-build"
			for success_tag in self.extra_data["koji_success_tags"]:
				koji_tagbuild_cmd = f"{koji_tagbuild_basecmd} {success_tag} {image_config["image_name"]}-{image_config["release_version"]}-{image_config["image_release"]}"
				kurchu.util.run_command(koji_tagbuild_cmd.split(), logfile)
			self.lftp_mirror(
				image_config["image_name"],
				image_config["buildsys"],
				"koji",
				image_config["gather_url"],
				self.output_dir,
				image_config["target"],
			)
