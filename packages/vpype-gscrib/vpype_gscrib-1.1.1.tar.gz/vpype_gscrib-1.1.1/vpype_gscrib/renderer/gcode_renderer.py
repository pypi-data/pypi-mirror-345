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

from collections import deque
from datetime import datetime
from typing import List, Tuple
from importlib.metadata import version

from numpy import array
from typeguard import typechecked
from vpype import Document, LineCollection
from vpype_gscrib.config import RenderConfig
from vpype_gscrib.processor import DocumentRenderer
from gscrib.gcode_builder import GCodeBuilder
from gscrib.enums.types import DistanceMode, FeedMode
from gscrib.enums.types import HaltMode, Plane
from gscrib.enums.units import TemperatureUnits
from vpype_gscrib.enums import *

from .gcode_context import GContext
from .fans import FanFactory
from .heads import HeadFactory
from .tools import ToolFactory
from .coolants import CoolantFactory
from .racks import RackFactory
from .beds import BedFactory


HEAD_SEPARATOR = "=" * 60
SECTION_SEPARATOR = "-" * 60


class GRenderer(DocumentRenderer):
    """Converts vector graphics to G-Code machine instructions.

    This class implements the `DocumentRenderer` interface by delegating
    specific machine operations to specialized components:

    - Head: Controls machine head movements (travel, plunge, retract)
    - Tool: Manages tool operations (tool activation/deactivation)
    - Coolant: Handles coolant system control (turn on/off)
    - Rack: Manages tool changes and rack operations
    - Bed: Handles bed operations (heat/cool down)

    Each component is created through its respective factory based on
    the configuration modes, allowing different strategies to be swapped
    without changing the renderer's core logic. This allows for:

    - Easy addition of new machine head types
    - Support for different tool systems (laser, spindle, etc.)
    - Flexible coolant control strategies
    - Various tool rack configurations

    The renderer coordinates these components to process the document
    hierarchy: Document → Layers → Paths → Segments, generating
    appropriate G-code commands through the `GCodeBuilder` instance.

    Args:
        builder (GCodeBuilder): G-code builder instance
        configs (List[RenderConfig]): Configuration parameters

    Attributes:
        _g (GCodeBuilder): G-code command builder instance
        _config (RenderConfig): Rendering configuration parameters
        _context (GContext): Current rendering context
        _head (BaseHead): Machine head controller
        _tool (BaseTool): Tool controller (laser, spindle, etc.)
        _coolant (BaseCoolant): Coolant system controller
        _rack (BaseRack): Tool rack controller
        _bed (BaseBed): Bed controller
        _fan (BaseFan): Fan controller
    """

    __slots__ = (
        "_g",
        "_ctx_queue",
        "_document_context",
        "_context",
        "_head_type",
        "_tool_type",
        "_coolant_type",
        "_rack_type",
        "_bed_type",
        "_fan_type",
    )

    @typechecked
    def __init__(self, builder: GCodeBuilder, configs: List[RenderConfig]):
        """G-code renderer initialization.

        Args:
            builder (GCodeBuilder): G-code builder instance
            config (List[RenderConfig]): Configuration parameters
        """

        self._g: GCodeBuilder = builder
        self._ctx_queue = self._build_contexts(builder, configs)
        self._document_context = self._switch_context()
        self._context = self._document_context

    def _switch_context(self) -> GContext:
        """Switch to the next context in the queue."""

        context = self._ctx_queue[0]

        self._context = context
        self._head_type = HeadFactory.create(context.head_type)
        self._tool_type = ToolFactory.create(context.tool_type)
        self._coolant_type = CoolantFactory.create(context.coolant_type)
        self._rack_type = RackFactory.create(context.rack_type)
        self._bed_type = BedFactory.create(context.bed_type)
        self._fan_type = FanFactory.create(context.fan_type)
        self._ctx_queue.rotate(-1)

        self._g.set_resolution(context.resolution)

        return context

    def _previous_context(self) -> GContext:
        """Get the previous context in the queue."""

        return (
            self._ctx_queue[-2] if
            len(self._ctx_queue) > 1 else
            self._ctx_queue[0]
        )

    @typechecked
    def begin_document(self, document: Document):
        """This method is invoked once per document before any of the
        document layers are processed.

        Initializes the G-code generation environment by:

        - Setting up the coordinate system
        - Configuring absolute positioning
        - Setting the appropriate unit system
        - Establishing the XY plane
        - Applying initial transformations for document orientation

        Args:
            document (Document): Document being processed
        """

        length_units = self._context.length_units
        time_units = self._context.time_units
        width, height = document.page_size

        self._write_document_header(document)
        self._write_user_header()

        self._g.set_distance_mode(DistanceMode.ABSOLUTE)
        self._g.set_feed_mode(FeedMode.UNITS_PER_MINUTE)
        self._g.set_temperature_units(TemperatureUnits.CELSIUS)
        self._g.set_length_units(length_units)
        self._g.set_time_units(time_units)
        self._g.set_plane(Plane.XY)

        self._g.transform.mirror(plane="zx")
        self._g.transform.translate(0, height)
        self._g.transform.scale(length_units.scale_factor)

        self._bed_type.turn_on(self._context)

    @typechecked
    def begin_layer(self, layer: LineCollection):
        """Each layer is composed of one or more paths. This method is
        invoked once per layer before any paths are processed.

        Prepares the machine for processing a new layer by:

        - Moving to service position for tool changes
        - Performing necessary tool changes
        - Positioning at the layer start point
        - Activating the tool and coolant systems

        Args:
            layer (LineCollection): Layer being processed
        """

        self._context = self._switch_context()

        first_path = self._first_path_of_layer(layer)
        x, y = self._first_point_of_path(first_path)
        self._write_layer_header(layer)

        self._head_type.park_for_service(self._context)
        self._rack_type.change_tool(self._context)

        self._head_type.safe_retract(self._context)
        self._head_type.travel_to(self._context, x, y)
        self._tool_type.activate(self._context)
        self._coolant_type.turn_on(self._context)
        self._fan_type.turn_on(self._context)

    @typechecked
    def begin_path(self, path: array):
        """Each path is composed of one or more segments. This method is
        invoked once per path before any of its segments are processed.

        Prepares for machining operations by:

        - Retracting the tool head
        - Moving to the path start position
        - Plunging to working depth
        - Activating tool power

        Args:
            path (array): Path being processed
        """

        x, y = self._first_point_of_path(path)

        self._head_type.retract(self._context)
        self._head_type.travel_to(self._context, x, y)
        self._head_type.plunge(self._context)
        self._tool_type.power_on(self._context)

    @typechecked
    def trace_segment(self, path: array, x: float, y: float):
        """This method is called once per segment within a path,
        receiving the segment's x and y coordinates.

        Generates G-code movement commands to trace the segment at the
        configured work speed with active tool settings.

        Args:
            path (array): Complete path being traced
            x (float): Target X coordinate of the segment
            y (float): Target Y coordinate of the segment
        """

        # Splits the current segment into smaller ones where the surface
        # height varies significantly (based on tolerance). If no height
        # map is available, the segment is traced as is.

        ctx = self._context
        cx, cy, cz = self._g.position

        for x, y, z in ctx.height_map.sample_path([cx, cy, x, y])[1:]:
            tool_params = self._tool_type.get_trace_params(ctx, x, y)
            self._head_type.trace_to(ctx, x, y, tool_params)

    @typechecked
    def end_path(self, path: array):
        """This method is invoked once per path after all segments of
        the path have been processed.

        Performs path completion operations:

        - Turning off tool power
        - Retracting the tool head to safe height

        Args:
            path (array): Path being processed
        """

        self._tool_type.power_off(self._context)
        self._head_type.retract(self._context)

    @typechecked
    def end_layer(self, layer: LineCollection):
        """This method is invoked once per layer after all paths on the
        layer have been processed.

        Performs layer cleanup operations:

        - Retracting to safe height
        - Deactivating the tool
        - Turning off coolant systems

        Args:
            layer (LineCollection): Layer being processed
        """

        self._head_type.safe_retract(self._context)
        self._tool_type.deactivate(self._context)
        self._fan_type.turn_off(self._context)
        self._coolant_type.turn_off(self._context)

    @typechecked
    def end_document(self, document: Document):
        """This method is invoked once per document after all layers on
        the document have been processed.

        Finalizes G-code generation by:

        - Moving to final park position
        - Adding program end commands
        - Performing cleanup operations

        Args:
            document (Document): Document being processed
        """

        self._context = self._document_context
        self._bed_type.turn_off(self._context)
        self._head_type.park_for_service(self._context)

        self._write_user_footer()
        self._g.halt(HaltMode.END_WITHOUT_RESET)
        self._g.teardown()

    @typechecked
    def process_error(self, e: Exception):
        """Invoked if an error occurs during the processing.

        Handles error conditions by:

        - Generating emergency stop commands
        - Performing safe shutdown procedures
        - Adding error information to the G-code output

        Args:
            e (Exception): The exception that occurred
        """

        self._g.emergency_halt(str(e))
        self._g.teardown()

    def _build_contexts(self, builder: GCodeBuilder, configs: List[RenderConfig]) -> deque:
        """Builds a context queue from a list of configurations."""

        return deque([GContext(builder, c) for c in configs])

    def _first_path_of_layer(self, layer: LineCollection) -> array:
        """Get the first path to render from a layer."""

        return layer.lines[0]

    def _first_point_of_path(self, path: array) -> Tuple[float, float]:
        """Coordinates of the first point to render from a path."""

        return path[0].real, path[0].imag

    def _write_user_header(self):
        """Write user-defined G-code header."""

        if self._document_context.header_gcode is not None:
            path = self._document_context.header_gcode
            self._write_include_file(path)

    def _write_user_footer(self):
        """Write user-defined G-code footer."""

        if self._document_context.footer_gcode is not None:
            path = self._document_context.footer_gcode
            self._write_include_file(path)

    def _write_document_header(self, document: Document):
        """Write document information as G-code header comments."""

        generator = f"vpype-gscrib {version('vpype_gscrib')}"
        iso_datetime = datetime.now().isoformat()
        num_layers = len(document.layers)

        self._g.comment(HEAD_SEPARATOR)
        self._g.comment(f"Date: {iso_datetime}")
        self._g.comment(f"Generated by: {generator}")
        self._g.comment(f"Vpype version: {version('vpype')}")
        self._g.comment(f"Gscrib version: {version('gscrib')}")
        self._g.comment("Program zero: bottom-left")
        self._g.comment(f"Number of layers: {num_layers}")
        self._write_document_config_info()
        self._g.comment(HEAD_SEPARATOR)

    def _write_layer_header(self, layer: LineCollection):
        """Write layer configuration as G-code comments."""

        layer_name = layer.property("vp_name")
        previous_ctx = self._previous_context()

        self._g.comment(SECTION_SEPARATOR)
        self._g.comment(f"Layer: {layer_name}")
        self._write_layer_config_info(self._context, previous_ctx)
        self._g.comment(SECTION_SEPARATOR)

    def _write_document_config_info(self):
        """Write configuration changes as G-code comments."""

        document_ctx = self._document_context
        document_values = document_ctx.format_config_values()

        self._g.comment(SECTION_SEPARATOR)

        for key, value in document_values.items():
            self._g.comment(f"@set {key} = {value}")

    def _write_layer_config_info(self,
        current_ctx: GContext, previous_ctx: GContext):
        """Write configuration changes as G-code comments."""

        document_ctx = self._document_context
        document_values = document_ctx.format_config_values().items()
        previous_values = previous_ctx.format_config_values().items()
        current_values = current_ctx.format_config_values().items()

        changed_settings = {
            key: value
            for key, value in current_values
            if (key, value) not in document_values
            or (key, value) not in previous_values
        }

        if len(changed_settings) > 0:
            self._g.comment(SECTION_SEPARATOR)

            for key, value in changed_settings.items():
                self._g.comment(f"@set {key} = {value}")

    def _write_include_file(self, path: str) -> None:
        """Write an include file as G-code comments."""

        with open(path, encoding="utf-8") as f:
            for line in f.readlines():
                self._g.write(line)
