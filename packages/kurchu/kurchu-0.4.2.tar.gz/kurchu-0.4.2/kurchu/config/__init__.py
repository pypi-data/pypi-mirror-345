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
import datetime
import tomllib


def generate_compose_date(date_format: str) -> str:
	"""Generate a compose date with the specified format"""
	return datetime.datetime.now(datetime.timezone.utc).strftime(date_format)


def read_config(config_filepath: Path) -> dict:
	"""Read the kurchu TOML config and return a dictionary"""
	config_data = {}
	with open(config_filepath, "r") as config_file:
		config_data = tomllib.loads(config_file.read())
	return config_data


def __process_gather_config(config: dict, format_args: dict) -> dict:
	"""Apply all string substitutions to generate configuration for gather section"""
	# Check if gather section exists
	if "gather" not in config["compose"].keys():
		return config
	# Create config dictionary
	final_config = config
	# Finalize sources
	for sources_index in range(len(final_config["compose"]["gather"]["sources"])):
		final_config["compose"]["gather"]["sources"][sources_index]["name"] = final_config["compose"]["gather"][
			"sources"
		][sources_index]["name"].format(**format_args)
		source_format_args = format_args | {"name": final_config["compose"]["gather"]["sources"][sources_index]["name"]}
		final_config["compose"]["gather"]["sources"][sources_index]["url"] = final_config["compose"]["gather"][
			"sources"
		][sources_index]["url"].format(**source_format_args)
		final_config["compose"]["gather"]["sources"][sources_index]["target"] = final_config["compose"]["gather"][
			"sources"
		][sources_index]["target"].format(**source_format_args)
	return final_config


def __process_compile_config(config: dict, format_args: dict) -> dict:
	"""Apply all string substitutions to generate configuration for compile section"""
	# Check if compile section exists
	if "compile" not in config["compose"].keys():
		return config
	# Create config dictionary
	final_config = config
	# Finalize image settings
	final_config["compose"]["compile"]["image_release"] = final_config["compose"]["compile"]["image_release"].format(
		**format_args
	)
	# Populate image targets
	image_format_args = format_args | {
		"base_name": final_config["compose"]["compile"]["base_name"],
		"image_release": final_config["compose"]["compile"]["image_release"],
	}
	for images_index in range(len(final_config["compose"]["compile"]["images"])):
		images_buildsys = final_config["compose"]["compile"]["images"][images_index]["buildsys"]
		final_config["compose"]["compile"]["images"][images_index]["gather_url"] = final_config["compose"]["compile"][
			"buildsys"
		][images_buildsys]["gather_url"]
		image_variant_format_args = image_format_args | {
			"variant": final_config["compose"]["compile"]["images"][images_index]["variant"]
		}
		final_config["compose"]["compile"]["images"][images_index]["image_name"] = "{base_name}-{variant}".format(
			**image_variant_format_args
		)
		image_variant_format_args = image_variant_format_args | {
			"image_name": final_config["compose"]["compile"]["images"][images_index]["image_name"]
		}
		final_config["compose"]["compile"]["images"][images_index]["target"] = final_config["compose"]["compile"][
			"target"
		].format(**image_variant_format_args)
		for images_prop in final_config["compose"]["compile"]["images"][images_index].keys():
			final_config["compose"]["compile"]["images"][images_index][images_prop] = final_config["compose"][
				"compile"
			]["images"][images_index][images_prop].format(**image_variant_format_args)
	# Delete no longer used gather_urls
	for buildsys_prop in final_config["compose"]["compile"]["buildsys"].keys():
		del final_config["compose"]["compile"]["buildsys"][buildsys_prop]["gather_url"]
	# Delete no longer used target
	del final_config["compose"]["compile"]["target"]
	# Finalize image definition configuration
	if "kiwi_result_bundle_name_format" in final_config["compose"]["compile"]["image_tool"]["kiwi"]:
		final_config["compose"]["compile"]["image_tool"]["kiwi"]["kiwi_result_bundle_name_format"].format(
			**image_format_args
		)
	for kiwi_config_prop in final_config["compose"]["compile"]["image_tool"]["kiwi"]["kiwi_description"].keys():
		final_config["compose"]["compile"]["image_tool"]["kiwi"]["kiwi_description"][kiwi_config_prop] = final_config[
			"compose"
		]["compile"]["image_tool"]["kiwi"]["kiwi_description"][kiwi_config_prop].format(**image_format_args)
	# Finalize buildsys
	for buildsys_key in final_config["compose"]["compile"]["buildsys"].keys():
		for buildsys_prop in final_config["compose"]["compile"]["buildsys"][buildsys_key].keys():
			if isinstance(final_config["compose"]["compile"]["buildsys"][buildsys_key][buildsys_prop], list):
				for buildsys_prop_list_index in range(
					len(final_config["compose"]["compile"]["buildsys"][buildsys_key][buildsys_prop])
				):
					final_config["compose"]["compile"]["buildsys"][buildsys_key][buildsys_prop][
						buildsys_prop_list_index
					] = final_config["compose"]["compile"]["buildsys"][buildsys_key][buildsys_prop][
						buildsys_prop_list_index
					].format(**image_format_args)
			else:
				final_config["compose"]["compile"]["buildsys"][buildsys_key][buildsys_prop] = final_config["compose"][
					"compile"
				]["buildsys"][buildsys_key][buildsys_prop].format(**image_format_args)
	return final_config


def __process_furnish_config(config: dict, format_args: dict) -> dict:
	"""Apply all string substitutions to generate configuration for furnish section"""
	# Check if compile section exists
	if "furnish" not in config["compose"].keys():
		return config
	# Create config dictionary
	final_config = config
	# TODO: Revisit once more settings are in place
	return final_config


def process_config(config: dict) -> dict:
	"""Apply all string substitutions to generate final runtime configuration"""
	# Create config dictionary
	final_config = config
	# Set basic values
	final_config["compose"]["compose_date"] = generate_compose_date(
		final_config["compose"]["date_format"] if "date_format" in final_config["compose"].keys() else "%Y%m%d"
	)
	final_config["compose"]["compose_id"] = config["compose"]["compose_id"].format(
		release_version=final_config["compose"]["release_version"], compose_date=final_config["compose"]["compose_date"]
	)
	main_format_args = {
		"release_version": final_config["compose"]["release_version"],
		"release_name": final_config["compose"]["release_name"],
		"compose_date": final_config["compose"]["compose_date"],
		"compose_id": final_config["compose"]["compose_id"],
	}
	# Finalize gather section
	final_config = __process_gather_config(final_config, main_format_args)
	# Finalize compile section
	final_config = __process_compile_config(final_config, main_format_args)
	# Finalize furnish section
	final_config = __process_furnish_config(final_config, main_format_args)
	return final_config
