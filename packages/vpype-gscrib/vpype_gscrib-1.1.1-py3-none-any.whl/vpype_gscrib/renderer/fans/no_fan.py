# -*- coding: utf-8 -*-

# G-Code generator for Vpype.
# Copyright (C) 2025 Joan Sala <contact@joansala.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from vpype_gscrib.renderer.gcode_context import GContext
from .base_fan import BaseFan


class NoFan(BaseFan):
    """No-op machine fan implementation.

    This class does not perform any fan operations, effectively
    disabling fan control.
    """

    def turn_on(self, ctx: GContext):
        pass

    def turn_off(self, ctx: GContext):
        pass
