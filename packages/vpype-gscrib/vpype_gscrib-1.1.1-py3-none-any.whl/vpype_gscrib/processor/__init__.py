# -*- coding: utf-8 -*-

"""
Vector graphics preprocessing for G-code generation.

This module provides the core functionality and interface for processing
and rendering `vpype` documents. It is used by the `vpype_gscrib.renderer`
module to produce the G-Code programs.
"""

from .document_processor import DocumentProcessor
from .document_renderer import DocumentRenderer

__all__ = [
    "DocumentProcessor",
    "DocumentRenderer",
]
