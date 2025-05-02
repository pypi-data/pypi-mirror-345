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

from gscrib.enums import HaltMode, TemperatureUnits
from vpype_gscrib.renderer.gcode_context import GContext
from .base_bed import BaseBed


class HeatedBed(BaseBed):
    """Heated bed implementation.

    This class handles the functionality for heated beds. It sets the
    bed target temperature when the bed is turned on and waits for the
    target to be reached. Sets the temperature to zero when turned off.
    """

    def turn_on(self, ctx: GContext):
        halt_mode = HaltMode.WAIT_FOR_BED
        ctx.g.set_bed_temperature(ctx.bed_temperature)
        ctx.g.halt(halt_mode, S=ctx.bed_temperature)

    def turn_off(self, ctx: GContext):
        ctx.g.set_bed_temperature(0)
