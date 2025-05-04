# exceptions.py - centralised error hierarchy for the Aztec tool
"""Hierarchy of exceptions used throughout the Aztec-tool project.

All project-specific errors inherit from :class:`AztecDecoderError`.  Each
sub-class is tailored to a distinct stage of the pipeline so that the caller
can catch an entire family (e.g. *any* RS-related error) or a single precise
issue (e.g. bit stuffing overflow).

Usage example
-------------
>>> try:
...     decoder = AztecDecoder(path)
...     msg = decoder.decode()
... except ReedSolomonError as err:
...     logger.error("RS decode failed: %s", err)
... except AztecDecoderError as err:
...     logger.error("Generic decode failure: %s", err)
"""
from __future__ import annotations

__all__ = [
    "AztecDecoderError",
    # configuration / parameters
    "InvalidParameterError",
    "UnsupportedSymbolError",
    # detection & image processing
    "BullseyeDetectionError",
    "OrientationError",
    # mode & layout
    "ModeFieldError",
    # bit extraction pipeline
    "BitReadError",
    "BitStuffingError",
    # error‑correction
    "ReedSolomonError",
    # high‑level decode
    "SymbolDecodeError",
    "StreamTerminationError",
]


class AztecDecoderError(Exception):
    """Base class for every exception raised by the Aztec decoder."""

class InvalidParameterError(AztecDecoderError):
    """One or more arguments passed to a function / constructor are invalid."""

class UnsupportedSymbolError(AztecDecoderError):
    """The symbol size or feature is outside the range handled by this library."""

class BullseyeDetectionError(AztecDecoderError):
    """Unable to locate or validate the bull's-eye pattern in the image."""


class OrientationError(AztecDecoderError):
    """The orientation markers are inconsistent or missing."""

class ModeFieldError(AztecDecoderError):
    """The *mode message* (layers, data words, ecc) is corrupt or undecodable."""

class BitReadError(AztecDecoderError):
    """Unexpected value or out-of-bounds access while reading raw modules."""
    
class BitStuffingError(AztecDecoderError):
    """Padding / bit-stuff pattern is malformed or inconsistent with the spec."""

class ReedSolomonError(AztecDecoderError):
    """Any failure raised by the Reed-Solomon decoder (wrapper class)."""

class SymbolDecodeError(AztecDecoderError):
    """A 5-bit (or 4-bit) symbol maps to no entry in the current table."""

class StreamTerminationError(AztecDecoderError):
    """End-of-stream reached prematurely or after unexpected extra data."""
