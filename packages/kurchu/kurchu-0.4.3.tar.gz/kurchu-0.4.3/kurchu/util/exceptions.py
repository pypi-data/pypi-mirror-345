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


class KurchuError(Exception):
	"""
	Base class for all exceptions

	All specific exceptions are subclasses of KurchuError.
	"""

	def __init__(self, message: str):
		self.message = message

	def __str__(self):
		return format(self.message)


class KurchuNonexistentPathError(KurchuError):
	"""
	Exception raised when attempting open a nonexistent path
	"""


class KurchuSourceSetupError(KurchuError):
	"""
	Exception raised when attempting to instantiate an unsupported
	source.
	"""


class KurchuUploadTargetSetupError(KurchuError):
	"""
	Exception raised when attempting to instantiate an unsupported
	upload target.
	"""


class KurchuBuildSysSetupError(KurchuError):
	"""
	Exception raised when attempting to instantiate an unsupported
	upload target.
	"""
