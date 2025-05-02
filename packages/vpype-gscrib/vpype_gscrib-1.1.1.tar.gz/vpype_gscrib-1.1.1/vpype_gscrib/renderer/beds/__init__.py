# -*- coding: utf-8 -*-

"""
Machine work area management.

This module provides implementations for controlling the machine's bed,
which serves as the foundational surface for machining or printing
operations. It may include G-code generation for various bed-related
functions, such as:

- Temperature control (heating and cooling)
- Work-holding mechanisms (e.g., vacuum, clamps)
- Bed leveling and compensation

It does not manage toolhead positioning during machining or printing
operations. Such motion is handled by the head component.
"""

from .base_bed import BaseBed
from .bed_factory import BedFactory
from .heated_bed import HeatedBed
from .no_bed import NoBed

__all__ = [
    "BaseBed",
    "BedFactory",
    "HeatedBed",
    "NoBed",
]
