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

from vpype_gscrib.enums import ToolType

from .base_tool import BaseTool
from .beam_tool import BeamTool
from .blade_tool import BladeTool
from .extruder_tool import ExtruderTool
from .heated_extruder_tool import HeatedExtruderTool
from .adaptive_beam_tool import AdaptiveBeamTool
from .marker_tool import MarkerTool
from .spindle_tool import SpindleTool


class ToolFactory:
    """A factory for creating tool managers.

    This factory creates specialized tool manager instances that handle
    different types of CNC machine tools and their operations. Each tool
    manager controls specific aspects of its corresponding tool such as
    power settings, speed, and operational states.
    """

    @classmethod
    def create(cls, tool_type: ToolType) -> BaseTool:
        """Create a new tool manger instance.

        Args:
            tool_type (ToolType): Tool type.

        Returns:
            BaseTool: Tool manger instance.

        Raises:
            KeyError: If type is not valid.
        """

        providers = {
            ToolType.BEAM: BeamTool,
            ToolType.BLADE: BladeTool,
            ToolType.EXTRUDER: ExtruderTool,
            ToolType.HEATED_EXTRUDER: HeatedExtruderTool,
            ToolType.ADAPTIVE_BEAM: AdaptiveBeamTool,
            ToolType.MARKER: MarkerTool,
            ToolType.SPINDLE: SpindleTool,
        }

        return providers[tool_type]()
